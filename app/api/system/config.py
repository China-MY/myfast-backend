from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.system.config import SysConfig
from app.domain.schemas.system.config import ConfigCreate, ConfigUpdate, ConfigInfo, ConfigQuery
from app.common.response import success, error, page
from app.service.system.config_service import (
    get_config, get_configs, create_config, update_config, delete_config, get_config_by_key
)

router = APIRouter()


@router.get("/list", summary="获取参数配置列表")
async def get_config_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: ConfigQuery = Depends(),
):
    """
    获取参数配置列表（分页查询）
    """
    try:
        configs, total = get_configs(db, params)
        config_list = [
            {
                "config_id": config.config_id,
                "config_name": config.config_name,
                "config_key": config.config_key,
                "config_value": config.config_value,
                "config_type": config.config_type,
                "create_time": config.create_time,
                "remark": config.remark
            }
            for config in configs
        ]
        return page(rows=config_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{config_id}", summary="获取参数配置详情")
async def get_config_info(
    config_id: int = Path(..., description="参数ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取参数配置详情
    """
    try:
        config = get_config(db, config_id)
        if not config:
            return error(msg="参数配置不存在", code=404)
        config_info = {
            "config_id": config.config_id,
            "config_name": config.config_name,
            "config_key": config.config_key,
            "config_value": config.config_value,
            "config_type": config.config_type,
            "create_time": config.create_time,
            "remark": config.remark
        }
        return success(data=config_info)
    except Exception as e:
        return error(msg=str(e))


@router.get("/key/{config_key}", summary="根据参数键名查询参数值")
async def get_config_value_by_key(
    config_key: str = Path(..., description="参数键名"),
    db: Session = Depends(get_db),
):
    """
    根据参数键名查询参数值
    """
    try:
        config = get_config_by_key(db, config_key)
        if not config:
            return error(msg="参数键名不存在", code=404)
        return success(data=config.config_value)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加参数配置")
async def add_config(
    config_data: ConfigCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加参数配置
    """
    try:
        config = create_config(db, config_data)
        return success(msg="参数配置添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改参数配置")
async def edit_config(
    config_data: ConfigUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改参数配置
    """
    try:
        config = update_config(db, config_data.config_id, config_data)
        return success(msg="参数配置修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{config_id}", summary="删除参数配置")
async def remove_config(
    config_id: int = Path(..., description="参数ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除参数配置
    """
    try:
        result = delete_config(db, config_id)
        return success(msg="参数配置删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 