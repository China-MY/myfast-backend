from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.system.dict_type import SysDictType
from app.domain.models.system.dict_data import SysDictData
from app.domain.schemas.system.dict_type import DictTypeCreate, DictTypeUpdate, DictTypeInfo, DictTypeQuery
from app.domain.schemas.system.dict_data import DictDataCreate, DictDataUpdate, DictDataInfo, DictDataQuery
from app.common.response import success, error, page
from app.service.system.dict_service import (
    get_dict_type, get_dict_types, create_dict_type, update_dict_type, delete_dict_type,
    get_dict_data, get_dict_datas, create_dict_data, update_dict_data, delete_dict_data,
    get_dict_datas_by_type
)

router = APIRouter()

# ========== 字典类型管理 ==========

@router.get("/type/list", summary="获取字典类型列表")
async def get_dict_type_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: DictTypeQuery = Depends(),
):
    """
    获取字典类型列表（分页查询）
    """
    try:
        dict_types, total = get_dict_types(db, params)
        dict_type_list = [
            {
                "dict_id": dict_type.dict_id,
                "dict_name": dict_type.dict_name,
                "dict_type": dict_type.dict_type,
                "status": dict_type.status,
                "create_time": dict_type.create_time,
                "remark": dict_type.remark
            }
            for dict_type in dict_types
        ]
        return page(rows=dict_type_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/type/info/{dict_id}", summary="获取字典类型详情")
async def get_dict_type_info(
    dict_id: int = Path(..., description="字典类型ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取字典类型详情
    """
    try:
        dict_type = get_dict_type(db, dict_id)
        if not dict_type:
            return error(msg="字典类型不存在", code=404)
        dict_type_info = {
            "dict_id": dict_type.dict_id,
            "dict_name": dict_type.dict_name,
            "dict_type": dict_type.dict_type,
            "status": dict_type.status,
            "create_time": dict_type.create_time,
            "remark": dict_type.remark
        }
        return success(data=dict_type_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/type/add", summary="添加字典类型")
async def add_dict_type(
    dict_type_data: DictTypeCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加字典类型
    """
    try:
        dict_type = create_dict_type(db, dict_type_data)
        return success(msg="字典类型添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/type/edit", summary="修改字典类型")
async def edit_dict_type(
    dict_type_data: DictTypeUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改字典类型
    """
    try:
        dict_type = update_dict_type(db, dict_type_data.dict_id, dict_type_data)
        return success(msg="字典类型修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/type/remove/{dict_id}", summary="删除字典类型")
async def remove_dict_type(
    dict_id: int = Path(..., description="字典类型ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除字典类型
    """
    try:
        result = delete_dict_type(db, dict_id)
        return success(msg="字典类型删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


# ========== 字典数据管理 ==========

@router.get("/data/list", summary="获取字典数据列表")
async def get_dict_data_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: DictDataQuery = Depends(),
):
    """
    获取字典数据列表（分页查询）
    """
    try:
        dict_datas, total = get_dict_datas(db, params)
        dict_data_list = [
            {
                "dict_code": dict_data.dict_code,
                "dict_sort": dict_data.dict_sort,
                "dict_label": dict_data.dict_label,
                "dict_value": dict_data.dict_value,
                "dict_type": dict_data.dict_type,
                "css_class": dict_data.css_class,
                "list_class": dict_data.list_class,
                "is_default": dict_data.is_default,
                "status": dict_data.status,
                "create_time": dict_data.create_time,
                "remark": dict_data.remark
            }
            for dict_data in dict_datas
        ]
        return page(rows=dict_data_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/data/info/{dict_code}", summary="获取字典数据详情")
async def get_dict_data_info(
    dict_code: int = Path(..., description="字典数据ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取字典数据详情
    """
    try:
        dict_data = get_dict_data(db, dict_code)
        if not dict_data:
            return error(msg="字典数据不存在", code=404)
        dict_data_info = {
            "dict_code": dict_data.dict_code,
            "dict_sort": dict_data.dict_sort,
            "dict_label": dict_data.dict_label,
            "dict_value": dict_data.dict_value,
            "dict_type": dict_data.dict_type,
            "css_class": dict_data.css_class,
            "list_class": dict_data.list_class,
            "is_default": dict_data.is_default,
            "status": dict_data.status,
            "create_time": dict_data.create_time,
            "remark": dict_data.remark
        }
        return success(data=dict_data_info)
    except Exception as e:
        return error(msg=str(e))


@router.get("/data/type/{dict_type}", summary="根据字典类型获取字典数据")
async def get_dict_data_by_type(
    dict_type: str = Path(..., description="字典类型"),
    db: Session = Depends(get_db),
):
    """
    根据字典类型获取字典数据
    """
    try:
        dict_datas = get_dict_datas_by_type(db, dict_type)
        dict_data_list = [
            {
                "dict_code": dict_data.dict_code,
                "dict_sort": dict_data.dict_sort,
                "dict_label": dict_data.dict_label,
                "dict_value": dict_data.dict_value,
                "dict_type": dict_data.dict_type,
                "css_class": dict_data.css_class,
                "list_class": dict_data.list_class,
                "is_default": dict_data.is_default,
                "status": dict_data.status
            }
            for dict_data in dict_datas
        ]
        return success(data=dict_data_list)
    except Exception as e:
        return error(msg=str(e))


@router.post("/data/add", summary="添加字典数据")
async def add_dict_data(
    dict_data_data: DictDataCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加字典数据
    """
    try:
        dict_data = create_dict_data(db, dict_data_data)
        return success(msg="字典数据添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/data/edit", summary="修改字典数据")
async def edit_dict_data(
    dict_data_data: DictDataUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改字典数据
    """
    try:
        dict_data = update_dict_data(db, dict_data_data.dict_code, dict_data_data)
        return success(msg="字典数据修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/data/remove/{dict_code}", summary="删除字典数据")
async def remove_dict_data(
    dict_code: int = Path(..., description="字典数据ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除字典数据
    """
    try:
        result = delete_dict_data(db, dict_code)
        return success(msg="字典数据删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 