from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.schemas.job import JobCreate, JobUpdate, JobOut, JobLogOut
from app.schemas.common import ResponseModel, PageResponseModel
from app.service.job import job_service

router = APIRouter()


@router.get("/list", response_model=PageResponseModel[List[JobOut]], summary="获取定时任务列表", description="分页获取定时任务列表")
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
    skip = (page - 1) * page_size
    jobs, total = job_service.get_jobs(
        db,
        skip=skip, 
        limit=page_size,
        job_name=job_name,
        job_group=job_group,
        status=status
    )
    
    return PageResponseModel[List[JobOut]](
        data=jobs,
        total=total,
        page=page,
        page_size=page_size
    )


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
    
    return ResponseModel[JobOut](data=job)


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
    job = job_service.create_job(db, job_in=job_in, creator_id=current_user.user_id)
    return ResponseModel[JobOut](data=job, msg="创建成功")


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
    
    job = job_service.update_job(db, job_id=job_id, job_in=job_in, updater_id=current_user.user_id)
    return ResponseModel[JobOut](data=job, msg="更新成功")


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


@router.get("/log/list", response_model=PageResponseModel[List[JobLogOut]], summary="获取任务日志列表", description="分页获取定时任务日志列表")
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
    skip = (page - 1) * page_size
    logs, total = job_service.get_job_logs(
        db,
        skip=skip, 
        limit=page_size,
        job_name=job_name,
        job_group=job_group,
        status=status
    )
    
    return PageResponseModel[List[JobLogOut]](
        data=logs,
        total=total,
        page=page,
        page_size=page_size
    )


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