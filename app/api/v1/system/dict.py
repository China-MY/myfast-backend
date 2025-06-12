from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.system.dict import dict_type as dict_type_crud
from app.crud.system.dict import dict_data as dict_data_crud
from app.schemas.system.dict import DictTypeCreate, DictTypeUpdate, DictDataCreate, DictDataUpdate
from app.schemas.system.dict import dict_type_to_dict, dict_data_to_dict
from app.schemas.utils.common import ResponseModel, PageResponseModel
from app.core.security import get_current_user_id

router = APIRouter()

# 字典类型接口
@router.get("/type/list", response_model=PageResponseModel)
def list_dict_types(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0),
    dict_name: Optional[str] = None,
    dict_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    获取字典类型列表(带分页)
    """
    skip = (page - 1) * page_size
    
    # 使用关联查询功能获取字典类型列表和对应的字典数据数量
    dict_types, total = dict_type_crud.get_with_dict_data_count(
        db, 
        skip=skip, 
        limit=page_size,
        dict_name=dict_name,
        dict_type=dict_type,
        status=status
    )
    
    # 格式化返回结果
    return {
        "code": 200,
        "msg": "操作成功",
        "rows": dict_types,
        "pageInfo": {
            "page": page,
            "pageSize": page_size,
            "total": total
        }
    }

@router.get("/type/all", response_model=ResponseModel)
def get_all_enabled_dict_types(*, db: Session = Depends(get_db)):
    """
    获取所有启用状态的字典类型列表
    """
    dict_types = dict_type_crud.get_enabled_dict_types(db)
    return {
        "code": 200,
        "msg": "操作成功",
        "data": dict_types
    }

@router.get("/type/{dict_id}", response_model=ResponseModel)
def get_dict_type(*, db: Session = Depends(get_db), dict_id: int = Path(...)):
    """
    根据ID获取字典类型详情
    """
    dict_type = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 获取关联的字典数据数量
    dict_data_count = db.query(dict_data_crud.model).filter(
        dict_data_crud.model.dict_type == dict_type.dict_type
    ).count()
    
    # 构建带有字典数据数量的响应
    dict_type_dict = dict_type_to_dict(dict_type)
    dict_type_dict["dict_data_count"] = dict_data_count
    dict_type_with_count = dict_type_dict
    
    return {
        "code": 200,
        "msg": "操作成功",
        "data": dict_type_with_count
    }

@router.post("/type", response_model=ResponseModel)
def create_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_type_in: DictTypeCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    创建字典类型
    """
    # 检查类型是否存在
    db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_type_in.dict_type)
    if db_dict_type:
        raise HTTPException(status_code=400, detail="字典类型已存在")
    
    # 创建字典类型
    dict_type = dict_type_crud.create_with_creator(
        db=db, obj_in=dict_type_in, creator_id=current_user_id
    )
    
    # 将SQLAlchemy模型转换为字典以便序列化
    dict_type_data = dict_type_to_dict(dict_type)
    
    return {
        "code": 200,
        "msg": "创建成功",
        "data": dict_type_data
    }

@router.put("/type/{dict_id}", response_model=ResponseModel)
def update_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_id: int = Path(...),
    dict_type_in: DictTypeUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    更新字典类型
    """
    # 检查字典类型是否存在
    dict_type = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 如果修改了dict_type，需要检查是否与其他记录冲突
    if dict_type_in.dict_type and dict_type_in.dict_type != dict_type.dict_type:
        is_duplicate = dict_type_crud.is_duplicate(
            db, dict_id=dict_id, dict_type=dict_type_in.dict_type
        )
        if is_duplicate:
            raise HTTPException(status_code=400, detail="字典类型已存在")
    
    # 更新字典类型
    dict_type = dict_type_crud.update_with_updater(
        db=db, db_obj=dict_type, obj_in=dict_type_in, updater_id=current_user_id
    )
    
    # 将SQLAlchemy模型转换为字典以便序列化
    dict_type_data = dict_type_to_dict(dict_type)
    
    return {
        "code": 200,
        "msg": "更新成功",
        "data": dict_type_data
    }

@router.delete("/type/{dict_id}", response_model=ResponseModel)
def delete_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_id: int = Path(...)
):
    """
    删除字典类型
    """
    # 检查字典类型是否存在
    dict_type = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 检查是否有关联的字典数据
    dict_data_count = db.query(dict_data_crud.model).filter(
        dict_data_crud.model.dict_type == dict_type.dict_type
    ).count()
    
    if dict_data_count > 0:
        raise HTTPException(status_code=400, detail="该字典类型下有字典数据，无法删除")
    
    # 删除字典类型
    dict_type_crud.remove(db=db, dict_id=dict_id)
    
    return {
        "code": 200,
        "msg": "删除成功"
    }

# 字典数据接口
@router.get("/data/list", response_model=PageResponseModel)
def list_dict_data(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0),
    dict_type: Optional[str] = None,
    dict_label: Optional[str] = None,
    status: Optional[str] = None
):
    """
    获取字典数据列表(带分页)
    """
    # 验证dict_type是否存在
    if dict_type:
        db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_type)
        if not db_dict_type:
            raise HTTPException(status_code=404, detail="字典类型不存在")
    
    skip = (page - 1) * page_size
    dict_data, total = dict_data_crud.get_multi_with_filter(
        db, 
        skip=skip, 
        limit=page_size,
        dict_type=dict_type,
        dict_label=dict_label,
        status=status
    )
    
    # 将SQLAlchemy模型列表转换为字典列表
    dict_data_list = [dict_data_to_dict(item) for item in dict_data]
    
    # 格式化返回结果
    return {
        "code": 200,
        "msg": "操作成功",
        "rows": dict_data_list,
        "pageInfo": {
            "page": page,
            "pageSize": page_size,
            "total": total
        }
    }

@router.get("/data/type/{dict_type}", response_model=ResponseModel)
def get_dict_data_by_type(
    *,
    db: Session = Depends(get_db),
    dict_type: str = Path(...)
):
    """
    根据字典类型获取字典数据列表
    """
    # 验证dict_type是否存在
    db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_type)
    if not db_dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    dict_data = dict_data_crud.get_by_dict_type(db, dict_type=dict_type)
    
    # 将SQLAlchemy模型列表转换为字典列表
    dict_data_list = [dict_data_to_dict(item) for item in dict_data]
    
    return {
        "code": 200,
        "msg": "操作成功",
        "data": dict_data_list
    }

@router.get("/data/options/{dict_type}", response_model=ResponseModel)
def get_dict_data_options(
    *,
    db: Session = Depends(get_db),
    dict_type: str = Path(...)
):
    """
    根据字典类型获取选项列表，用于前端下拉选择
    """
    # 验证dict_type是否存在
    db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_type)
    if not db_dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    options = dict_data_crud.get_options_by_dict_type(db, dict_type=dict_type)
    
    return {
        "code": 200,
        "msg": "操作成功",
        "data": options
    }

@router.get("/data/{dict_code}", response_model=ResponseModel)
def get_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int = Path(...)
):
    """
    根据编码获取字典数据
    """
    dict_data = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    # 将SQLAlchemy模型转换为字典
    dict_data_dict = dict_data_to_dict(dict_data)
    
    return {
        "code": 200,
        "msg": "操作成功",
        "data": dict_data_dict
    }

@router.post("/data", response_model=ResponseModel)
def create_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_data_in: DictDataCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    创建字典数据
    """
    # 验证dict_type是否存在
    db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_data_in.dict_type)
    if not db_dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 验证同一字典类型下的字典值是否重复
    is_duplicate = dict_data_crud.is_duplicate(
        db, dict_type=dict_data_in.dict_type, dict_value=dict_data_in.dict_value
    )
    if is_duplicate:
        raise HTTPException(status_code=400, detail="字典键值已存在")
    
    # 创建字典数据
    dict_data = dict_data_crud.create_with_creator(
        db=db, obj_in=dict_data_in, creator_id=current_user_id
    )
    
    # 将SQLAlchemy模型转换为字典以便序列化
    dict_data_dict = dict_data_to_dict(dict_data)
    
    return {
        "code": 200,
        "msg": "创建成功",
        "data": dict_data_dict
    }

@router.put("/data/{dict_code}", response_model=ResponseModel)
def update_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int = Path(...),
    dict_data_in: DictDataUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    更新字典数据
    """
    # 检查字典数据是否存在
    dict_data = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    # 如果更新了字典类型，检查字典类型是否存在
    if dict_data_in.dict_type and dict_data_in.dict_type != dict_data.dict_type:
        db_dict_type = dict_type_crud.get_by_type(db, dict_type=dict_data_in.dict_type)
        if not db_dict_type:
            raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 如果修改了dict_value，检查是否与同一类型下的其他记录冲突
    if dict_data_in.dict_value and dict_data_in.dict_value != dict_data.dict_value:
        dict_type = dict_data_in.dict_type or dict_data.dict_type
        is_duplicate = dict_data_crud.is_duplicate(
            db, 
            dict_code=dict_code,
            dict_type=dict_type,
            dict_value=dict_data_in.dict_value
        )
        if is_duplicate:
            raise HTTPException(status_code=400, detail="字典键值已存在")
    
    # 更新字典数据
    dict_data = dict_data_crud.update_with_updater(
        db=db, db_obj=dict_data, obj_in=dict_data_in, updater_id=current_user_id
    )
    
    # 将SQLAlchemy模型转换为字典以便序列化
    dict_data_dict = dict_data_to_dict(dict_data)
    
    return {
        "code": 200,
        "msg": "更新成功",
        "data": dict_data_dict
    }

@router.delete("/data/{dict_code}", response_model=ResponseModel)
def delete_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int = Path(...)
):
    """
    删除字典数据
    """
    # 检查字典数据是否存在
    dict_data = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    # 删除字典数据
    dict_data_crud.remove(db=db, dict_code=dict_code)
    
    return {
        "code": 200,
        "msg": "删除成功"
    } 