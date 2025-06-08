from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.schemas.config import ConfigCreate, ConfigUpdate, ConfigOut
from app.schemas.common import ResponseModel, PageResponseModel
from app.crud.config import config as config_crud

router = APIRouter()


@router.get("/list", response_model=PageResponseModel[List[ConfigOut]], summary="获取参数配置列表", description="分页获取参数配置列表")
def list_configs(
    db: Session = Depends(get_db),
    *,
    config_name: Optional[str] = None,
    config_key: Optional[str] = None,
    config_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["system:config:list"]))
) -> Any:
    """
    获取参数配置列表
    """
    skip = (page - 1) * page_size
    configs, total = config_crud.get_multi_with_filter(
        db, 
        skip=skip, 
        limit=page_size,
        config_name=config_name,
        config_key=config_key,
        config_type=config_type
    )
    
    return PageResponseModel[List[ConfigOut]](
        data=configs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{config_id}", response_model=ResponseModel[ConfigOut], summary="获取参数配置详情", description="根据参数ID获取参数配置详情")
def get_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    _: bool = Depends(check_permissions(["system:config:query"]))
) -> Any:
    """
    获取参数配置详情
    """
    config_obj = config_crud.get_by_id(db, config_id=config_id)
    if not config_obj:
        raise HTTPException(status_code=404, detail="参数配置不存在")
    
    return ResponseModel[ConfigOut](data=config_obj)


@router.get("/key/{config_key}", response_model=ResponseModel[str], summary="根据参数键名获取参数值", description="根据参数键名获取参数值")
def get_config_by_key(
    *,
    db: Session = Depends(get_db),
    config_key: str
) -> Any:
    """
    根据参数键名获取参数值
    """
    config_value = config_crud.get_config_value_by_key(db, config_key=config_key)
    if config_value is None:
        raise HTTPException(status_code=404, detail="参数键名不存在")
    
    return ResponseModel[str](data=config_value)


@router.post("", response_model=ResponseModel[ConfigOut], summary="创建参数配置", description="创建新参数配置")
def create_config(
    *,
    db: Session = Depends(get_db),
    config_in: ConfigCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:config:add"]))
) -> Any:
    """
    创建新参数配置
    """
    # 检查参数键名是否已存在
    if config_crud.get_by_key(db, config_key=config_in.config_key):
        raise HTTPException(status_code=400, detail="参数键名已存在")
    
    config_obj = config_crud.create(db, obj_in=config_in, creator_id=current_user.user_id)
    return ResponseModel[ConfigOut](data=config_obj, msg="创建成功")


@router.put("/{config_id}", response_model=ResponseModel[ConfigOut], summary="更新参数配置", description="更新参数配置信息")
def update_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    config_in: ConfigUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:config:edit"]))
) -> Any:
    """
    更新参数配置信息
    """
    config_obj = config_crud.get_by_id(db, config_id=config_id)
    if not config_obj:
        raise HTTPException(status_code=404, detail="参数配置不存在")
    
    # 检查参数键名唯一性
    if config_in.config_key and config_in.config_key != config_obj.config_key:
        if config_crud.get_by_key(db, config_key=config_in.config_key):
            raise HTTPException(status_code=400, detail="参数键名已存在")
    
    config_obj = config_crud.update(db, db_obj=config_obj, obj_in=config_in, updater_id=current_user.user_id)
    return ResponseModel[ConfigOut](data=config_obj, msg="更新成功")


@router.delete("/{config_id}", response_model=ResponseModel, summary="删除参数配置", description="删除指定参数配置")
def delete_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    _: bool = Depends(check_permissions(["system:config:remove"]))
) -> Any:
    """
    删除参数配置
    """
    config_obj = config_crud.get_by_id(db, config_id=config_id)
    if not config_obj:
        raise HTTPException(status_code=404, detail="参数配置不存在")
    
    # 检查参数是否为系统内置参数
    if config_obj.config_type == "Y":
        raise HTTPException(status_code=400, detail="系统内置参数不能删除")
    
    config_crud.remove(db, config_id=config_id)
    return ResponseModel(msg="删除成功")