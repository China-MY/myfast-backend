from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.crud.dict import dict_type as dict_type_crud
from app.crud.dict import dict_data as dict_data_crud
from app.schemas.dict import DictTypeCreate, DictTypeUpdate, DictTypeOut, DictDataCreate, DictDataUpdate, DictDataOut
from app.schemas.common import ResponseModel, PageResponseModel

router = APIRouter()

# 字典类型接口
@router.get("/type/list", response_model=PageResponseModel[List[DictTypeOut]], summary="获取字典类型列表", description="分页获取字典类型列表")
def list_dict_types(
    db: Session = Depends(get_db),
    *,
    dict_name: Optional[str] = None,
    dict_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["system:dict:list"]))
) -> Any:
    """
    获取字典类型列表
    """
    skip = (page - 1) * page_size
    dict_types, total = dict_type_crud.get_multi_with_filter(
        db, 
        skip=skip, 
        limit=page_size,
        dict_name=dict_name,
        dict_type=dict_type,
        status=status
    )
    
    return PageResponseModel[List[DictTypeOut]](
        data=dict_types,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/type/{dict_id}", response_model=ResponseModel[DictTypeOut], summary="获取字典类型详情", description="根据字典类型ID获取详情")
def get_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_id: int,
    _: bool = Depends(check_permissions(["system:dict:query"]))
) -> Any:
    """
    获取字典类型详情
    """
    dict_type_obj = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type_obj:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    return ResponseModel[DictTypeOut](data=dict_type_obj)


@router.post("/type", response_model=ResponseModel[DictTypeOut], summary="创建字典类型", description="创建新字典类型")
def create_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_type_in: DictTypeCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dict:add"]))
) -> Any:
    """
    创建新字典类型
    """
    # 检查字典类型是否已存在
    if dict_type_crud.get_by_type(db, dict_type=dict_type_in.dict_type):
        raise HTTPException(status_code=400, detail="字典类型已存在")
    
    # 检查字典名称是否已存在
    if dict_type_crud.get_by_name(db, dict_name=dict_type_in.dict_name):
        raise HTTPException(status_code=400, detail="字典名称已存在")
    
    dict_type_obj = dict_type_crud.create(db, obj_in=dict_type_in, creator_id=current_user.user_id)
    return ResponseModel[DictTypeOut](data=dict_type_obj, msg="创建成功")


@router.put("/type/{dict_id}", response_model=ResponseModel[DictTypeOut], summary="更新字典类型", description="更新字典类型信息")
def update_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_id: int,
    dict_type_in: DictTypeUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dict:edit"]))
) -> Any:
    """
    更新字典类型信息
    """
    dict_type_obj = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type_obj:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 检查字典类型唯一性
    if dict_type_in.dict_type and dict_type_in.dict_type != dict_type_obj.dict_type:
        if dict_type_crud.get_by_type(db, dict_type=dict_type_in.dict_type):
            raise HTTPException(status_code=400, detail="字典类型已存在")
    
    # 检查字典名称唯一性
    if dict_type_in.dict_name and dict_type_in.dict_name != dict_type_obj.dict_name:
        if dict_type_crud.get_by_name(db, dict_name=dict_type_in.dict_name):
            raise HTTPException(status_code=400, detail="字典名称已存在")
    
    dict_type_obj = dict_type_crud.update(db, db_obj=dict_type_obj, obj_in=dict_type_in, updater_id=current_user.user_id)
    return ResponseModel[DictTypeOut](data=dict_type_obj, msg="更新成功")


@router.delete("/type/{dict_id}", response_model=ResponseModel, summary="删除字典类型", description="删除指定字典类型")
def delete_dict_type(
    *,
    db: Session = Depends(get_db),
    dict_id: int,
    _: bool = Depends(check_permissions(["system:dict:remove"]))
) -> Any:
    """
    删除字典类型
    """
    dict_type_obj = dict_type_crud.get_by_id(db, dict_id=dict_id)
    if not dict_type_obj:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    # 检查是否有关联的字典数据
    if dict_type_crud.has_dict_data(db, dict_type=dict_type_obj.dict_type):
        raise HTTPException(status_code=400, detail="字典类型已分配，不能删除")
    
    dict_type_crud.remove(db, dict_id=dict_id)
    return ResponseModel(msg="删除成功")


@router.get("/type/options", response_model=ResponseModel[List[DictTypeOut]], summary="获取字典类型选项", description="获取字典类型选项列表")
def get_dict_type_options(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取字典类型选项列表
    """
    dict_types = dict_type_crud.get_enabled_dict_types(db)
    return ResponseModel[List[DictTypeOut]](data=dict_types)


# 字典数据接口
@router.get("/data/list", response_model=PageResponseModel[List[DictDataOut]], summary="获取字典数据列表", description="分页获取字典数据列表")
def list_dict_data(
    db: Session = Depends(get_db),
    *,
    dict_type: Optional[str] = None,
    dict_label: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["system:dict:list"]))
) -> Any:
    """
    获取字典数据列表
    """
    skip = (page - 1) * page_size
    dict_data, total = dict_data_crud.get_multi_with_filter(
        db, 
        skip=skip, 
        limit=page_size,
        dict_type=dict_type,
        dict_label=dict_label,
        status=status
    )
    
    return PageResponseModel[List[DictDataOut]](
        data=dict_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/data/type/{dict_type}", response_model=ResponseModel[List[DictDataOut]], summary="根据字典类型获取字典数据", description="根据字典类型获取字典数据列表")
def get_dict_data_by_type(
    *,
    db: Session = Depends(get_db),
    dict_type: str
) -> Any:
    """
    根据字典类型获取字典数据列表
    """
    dict_data = dict_data_crud.get_by_dict_type(db, dict_type=dict_type)
    return ResponseModel[List[DictDataOut]](data=dict_data)


@router.get("/data/{dict_code}", response_model=ResponseModel[DictDataOut], summary="获取字典数据详情", description="根据字典编码获取字典数据详情")
def get_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int,
    _: bool = Depends(check_permissions(["system:dict:query"]))
) -> Any:
    """
    获取字典数据详情
    """
    dict_data_obj = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data_obj:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    return ResponseModel[DictDataOut](data=dict_data_obj)


@router.post("/data", response_model=ResponseModel[DictDataOut], summary="创建字典数据", description="创建新字典数据")
def create_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_data_in: DictDataCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dict:add"]))
) -> Any:
    """
    创建新字典数据
    """
    # 检查字典类型是否存在
    if not dict_type_crud.get_by_type(db, dict_type=dict_data_in.dict_type):
        raise HTTPException(status_code=400, detail="字典类型不存在")
    
    # 检查字典键值和标签在同一类型下是否唯一
    if dict_data_crud.is_duplicate(db, dict_type=dict_data_in.dict_type, dict_value=dict_data_in.dict_value, dict_label=dict_data_in.dict_label):
        raise HTTPException(status_code=400, detail="字典键值或标签已存在于该类型下")
    
    dict_data_obj = dict_data_crud.create(db, obj_in=dict_data_in, creator_id=current_user.user_id)
    return ResponseModel[DictDataOut](data=dict_data_obj, msg="创建成功")


@router.put("/data/{dict_code}", response_model=ResponseModel[DictDataOut], summary="更新字典数据", description="更新字典数据信息")
def update_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int,
    dict_data_in: DictDataUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dict:edit"]))
) -> Any:
    """
    更新字典数据信息
    """
    dict_data_obj = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data_obj:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    # 检查字典类型是否存在
    if dict_data_in.dict_type and dict_data_in.dict_type != dict_data_obj.dict_type:
        if not dict_type_crud.get_by_type(db, dict_type=dict_data_in.dict_type):
            raise HTTPException(status_code=400, detail="字典类型不存在")
    
    # 检查字典键值和标签在同一类型下是否唯一
    dict_type = dict_data_in.dict_type if dict_data_in.dict_type else dict_data_obj.dict_type
    dict_value = dict_data_in.dict_value if dict_data_in.dict_value else dict_data_obj.dict_value
    dict_label = dict_data_in.dict_label if dict_data_in.dict_label else dict_data_obj.dict_label
    
    if dict_data_crud.is_duplicate(db, dict_type=dict_type, dict_value=dict_value, dict_label=dict_label, exclude_id=dict_code):
        raise HTTPException(status_code=400, detail="字典键值或标签已存在于该类型下")
    
    dict_data_obj = dict_data_crud.update(db, db_obj=dict_data_obj, obj_in=dict_data_in, updater_id=current_user.user_id)
    return ResponseModel[DictDataOut](data=dict_data_obj, msg="更新成功")


@router.delete("/data/{dict_code}", response_model=ResponseModel, summary="删除字典数据", description="删除指定字典数据")
def delete_dict_data(
    *,
    db: Session = Depends(get_db),
    dict_code: int,
    _: bool = Depends(check_permissions(["system:dict:remove"]))
) -> Any:
    """
    删除字典数据
    """
    dict_data_obj = dict_data_crud.get_by_id(db, dict_code=dict_code)
    if not dict_data_obj:
        raise HTTPException(status_code=404, detail="字典数据不存在")
    
    dict_data_crud.remove(db, dict_code=dict_code)
    return ResponseModel(msg="删除成功") 