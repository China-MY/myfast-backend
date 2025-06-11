from typing import Any, List, Optional, Dict, TypeVar, Generic, Type
import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.schemas.job import JobCreate, JobUpdate, JobOut, JobLogOut
from app.schemas.common import ResponseModel, PageResponseModel, PageInfo
from app.service.job import job_service


def sqlalchemy_to_pydantic(obj: Any, model_class: Type) -> Any:
    """将SQLAlchemy对象转换为Pydantic模型对象
    
    Args:
        obj: SQLAlchemy对象或任何可序列化对象
        model_class: Pydantic模型类
        
    Returns:
        转换后的Pydantic模型对象
    """
    print(f"[DEBUG] sqlalchemy_to_pydantic - 输入对象类型: {type(obj)}")
    try:
        # 先检查obj是否为model_class的实例，如果是则直接返回
        if isinstance(obj, model_class):
            print(f"[DEBUG] 对象已经是目标类型: {model_class.__name__}")
            return obj
            
        # 如果obj是一个字典的items()视图或者元组列表，先转为字典
        if hasattr(obj, 'items') and callable(getattr(obj, 'items')):
            print(f"[DEBUG] 对象有items方法，尝试转为字典")
            obj_dict = dict(obj.items())
            return model_class.model_validate(obj_dict)
        
        # 如果对象有to_dict方法（我们自定义的）
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            obj_dict = obj.to_dict()
            print(f"[DEBUG] 使用to_dict方法转换为字典: {obj_dict}")
            return model_class.model_validate(obj_dict)
        
        # 如果是SQLAlchemy模型对象
        if hasattr(obj, '__table__'):
            print(f"[DEBUG] 检测到SQLAlchemy模型对象，处理中...")
            # 转换为字典
            obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            print(f"[DEBUG] 转换为字典: {obj_dict}")
            return model_class.model_validate(obj_dict)
        
        # 如果是元组且有_fields属性（namedtuple）
        if isinstance(obj, tuple):
            print(f"[DEBUG] 检测到元组对象: {obj}")
            # 如果只有两个元素，且第一个可能是键，第二个是值（键值对形式）
            if len(obj) == 2 and isinstance(obj[0], str):
                print(f"[DEBUG] 可能是单个键值对元组: {obj}")
                # 创建只包含这个键值对的字典
                return {obj[0]: obj[1]}
                
            if hasattr(obj, '_fields'):
                print(f"[DEBUG] namedtuple处理: _fields={obj._fields}")
                obj_dict = dict(zip(obj._fields, obj))
                return model_class.model_validate(obj_dict)
            else:
                # 对于普通元组，尝试识别属性值
                # 根据数据库表的结构尝试按顺序赋值
                print(f"[DEBUG] 处理普通元组，假设顺序与属性按SQLAlchemy模型顺序匹配")
                from app.models.job import SysJob
                # 获取SysJob表的所有列名
                columns = [c.name for c in SysJob.__table__.columns]
                
                # 如果元组长度与列数匹配，则按顺序映射
                if len(obj) == len(columns):
                    obj_dict = dict(zip(columns, obj))
                    print(f"[DEBUG] 处理普通元组，按列顺序匹配: {obj_dict}")
                    return model_class.model_validate(obj_dict)
                else:
                    print(f"[ERROR] 元组长度({len(obj)})与模型列数({len(columns)})不匹配")
                    print(f"[DEBUG] 将尝试使用索引访问元组字段...")
                    # 尝试通过索引访问
                    obj_dict = {}
                    # 根据实际返回的元组结构，手动映射关键字段
                    # 通常 job_id, job_name, job_group 等是最基本字段
                    if len(obj) > 0:
                        obj_dict["job_id"] = obj[0]
                    if len(obj) > 1:
                        obj_dict["job_name"] = obj[1]  
                    if len(obj) > 2:
                        obj_dict["job_group"] = obj[2]
                    if len(obj) > 3:
                        obj_dict["invoke_target"] = obj[3]
                    if len(obj) > 4:
                        obj_dict["cron_expression"] = obj[4]
                    if len(obj) > 5:
                        obj_dict["misfire_policy"] = obj[5]  
                    if len(obj) > 6:
                        obj_dict["concurrent"] = obj[6]
                    if len(obj) > 7:
                        obj_dict["status"] = obj[7]
                    if len(obj) > 8:
                        obj_dict["remark"] = obj[8]
                    if len(obj) > 9:
                        obj_dict["create_by"] = obj[9]
                    if len(obj) > 10:
                        obj_dict["create_time"] = obj[10]
                    if len(obj) > 11:
                        obj_dict["update_by"] = obj[11]
                    if len(obj) > 12:
                        obj_dict["update_time"] = obj[12]
                    
                    print(f"[DEBUG] 手动映射后的字典: {obj_dict}")
                    return model_class.model_validate(obj_dict)
        
        # 如果是字典
        if isinstance(obj, dict):
            return model_class.model_validate(obj)
        
        # 尝试使用__dict__属性
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__.copy()
            # 移除私有属性
            for key in list(obj_dict.keys()):
                if key.startswith('_'):
                    del obj_dict[key]
            return model_class.model_validate(obj_dict)
        
        # 尝试提取所有非私有、非可调用属性
        obj_dict = {k: getattr(obj, k) for k in dir(obj) 
                   if not k.startswith('_') and not callable(getattr(obj, k))}
        return model_class.model_validate(obj_dict)
    except Exception as e:
        print(f"Error converting object to Pydantic model: {e}, obj: {obj}")
        raise ValueError(f"Cannot convert object to Pydantic model: {e}")


router = APIRouter()


@router.get("/list", summary="获取定时任务列表", description="分页获取定时任务列表")
def list_jobs(
    db: Session = Depends(get_db),
    *,
    job_name: Optional[str] = None,
    job_group: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["monitor:job:list"]))
) -> Any:
    """
    获取定时任务列表
    """
    # 记录请求参数
    print(f"[DEBUG] list_jobs - 参数: job_name={job_name}, job_group={job_group}, status={status}, page={page}, page_size={page_size}")
    skip = (page - 1) * page_size
    print(f"[DEBUG] 调用 job_service.get_jobs 获取任务列表, skip={skip}, limit={page_size}")
    jobs, total = job_service.get_jobs(
        db,
        skip=skip, 
        limit=page_size,
        job_name=job_name,
        job_group=job_group,
        status=status
    )
    print(f"[DEBUG] job_service.get_jobs 返回，总计: {total}，数据类型: {type(jobs)}")
    
    # 直接构建为可序列化的字典
    rows = []
    for job in jobs:
        # SQLAlchemy模型对象转换为普通字典
        if hasattr(job, '__table__'):
            job_dict = {c.name: getattr(job, c.name) for c in job.__table__.columns}
            # 转换日期时间对象为ISO格式字符串
            for key, value in job_dict.items():
                if isinstance(value, datetime.datetime):
                    job_dict[key] = value.isoformat()
            rows.append(job_dict)
            print(f"[DEBUG] 转换SQLAlchemy对象到字典: {job_dict}")
    
    # 创建分页信息
    page_info = {
        "page": page,
        "pageSize": page_size,
        "total": total
    }
    
    # 构造JSON响应
    response_data = {
        "code": 200,
        "msg": "操作成功",
        "rows": rows,
        "pageInfo": page_info
    }
    
    # 直接返回字典，不使用Pydantic模型
    return response_data


@router.get("/{job_id}", response_model=ResponseModel[JobOut], summary="获取定时任务详情", description="根据任务ID获取定时任务详情")
def get_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    _: bool = Depends(check_permissions(["monitor:job:query"]))
) -> Any:
    """
    获取定时任务详情
    """
    job = job_service.get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    job_out = sqlalchemy_to_pydantic(job, JobOut)
    return ResponseModel[JobOut](data=job_out)


@router.post("", response_model=ResponseModel[JobOut], summary="创建定时任务", description="创建新定时任务")
def create_job(
    *,
    db: Session = Depends(get_db),
    job_in: JobCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["monitor:job:add"]))
) -> Any:
    """
    创建新定时任务
    """
    job = job_service.create_job(db, obj_in=job_in, current_user_id=current_user.user_id)
    job_out = sqlalchemy_to_pydantic(job, JobOut)
    return ResponseModel[JobOut](data=job_out, msg="创建成功")


@router.put("/{job_id}", response_model=ResponseModel[JobOut], summary="更新定时任务", description="更新定时任务信息")
def update_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    job_in: JobUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["monitor:job:edit"]))
) -> Any:
    """
    更新定时任务信息
    """
    job = job_service.get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    job = job_service.update_job(db, job_id=job_id, obj_in=job_in, current_user_id=current_user.user_id)
    job_out = sqlalchemy_to_pydantic(job, JobOut)
    return ResponseModel[JobOut](data=job_out, msg="更新成功")


@router.delete("/{job_id}", response_model=ResponseModel, summary="删除定时任务", description="删除指定定时任务")
def delete_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    _: bool = Depends(check_permissions(["monitor:job:remove"]))
) -> Any:
    """
    删除定时任务
    """
    job = job_service.get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    job_service.delete_job(db, job_id=job_id)
    return ResponseModel(msg="删除成功")


@router.put("/{job_id}/status/{status}", response_model=ResponseModel, summary="修改任务状态", description="修改定时任务状态")
def change_job_status(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    status: str,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["monitor:job:changeStatus"]))
) -> Any:
    """
    修改定时任务状态
    """
    if status not in ["0", "1"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    job = job_service.get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    job_service.change_job_status(db, job_id=job_id, status=status, updater_id=current_user.user_id)
    return ResponseModel(msg="状态修改成功")


@router.post("/{job_id}/run", response_model=ResponseModel, summary="执行定时任务", description="立即执行一次定时任务")
def run_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    _: bool = Depends(check_permissions(["monitor:job:changeStatus"]))
) -> Any:
    """
    立即执行一次定时任务
    """
    job = job_service.get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    job_service.run_job_once(db, job_id=job_id)
    return ResponseModel(msg="执行成功")


@router.get("/log/list", summary="获取任务日志列表", description="分页获取定时任务日志列表")
def list_job_logs(
    db: Session = Depends(get_db),
    *,
    job_name: Optional[str] = None,
    job_group: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["monitor:job:query"]))
) -> Any:
    """
    获取定时任务日志列表
    """
    print(f"[DEBUG] list_job_logs - 参数: job_name={job_name}, job_group={job_group}, status={status}, page={page}, page_size={page_size}")
    skip = (page - 1) * page_size
    logs, total = job_service.get_job_logs(
        db,
        skip=skip, 
        limit=page_size,
        job_name=job_name,
        job_group=job_group,
        status=status
    )
    
    # 直接构建为可序列化的字典
    rows = []
    for log in logs:
        # SQLAlchemy模型对象转换为普通字典
        if hasattr(log, '__table__'):
            log_dict = {c.name: getattr(log, c.name) for c in log.__table__.columns}
            # 转换日期时间对象为ISO格式字符串
            for key, value in log_dict.items():
                if isinstance(value, datetime.datetime):
                    log_dict[key] = value.isoformat()
            rows.append(log_dict)
            print(f"[DEBUG] 转换日志SQLAlchemy对象到字典: {log_dict}")
    
    # 创建分页信息
    page_info = {
        "page": page,
        "pageSize": page_size,
        "total": total
    }
    
    # 构造JSON响应
    response_data = {
        "code": 200,
        "msg": "操作成功",
        "rows": rows,
        "pageInfo": page_info
    }
    
    # 直接返回字典，不使用Pydantic模型
    return response_data


@router.delete("/log/clean", response_model=ResponseModel, summary="清空任务日志", description="清空所有定时任务日志")
def clean_job_logs(
    *,
    db: Session = Depends(get_db),
    _: bool = Depends(check_permissions(["monitor:job:remove"]))
) -> Any:
    """
    清空所有定时任务日志
    """
    count = job_service.clean_all_job_logs(db)
    return ResponseModel(data={"count": count}, msg=f"已清除{count}条日志") 