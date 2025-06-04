from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user, get_current_admin_user
from app.entity.sys_user import SysUser
from app.service.system.menu_service import MenuService
from app.common.response import ResponseModel, success_response, error_response

router = APIRouter()

@router.get("/", response_model=dict)
def get_menus(
    *,
    db: Session = Depends(get_db),
    menu_name: str = None,
    status: str = None,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单列表
    """
    menus = MenuService.get_menus(db, menu_name=menu_name, status=status)
    return ResponseModel.success(data=menus)

@router.get("/tree", response_model=dict)
def get_menu_tree(
    *,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单树
    """
    menu_tree = MenuService.get_menu_tree(db)
    return ResponseModel.success(data=menu_tree)

@router.post("/", response_model=dict)
def create_menu(
    *,
    db: Session = Depends(get_db),
    menu_data: Dict[str, Any],
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    创建菜单
    """
    menu = MenuService.create_menu(db, menu_data, current_user.username)
    return ResponseModel.success(data=menu)

@router.get("/{menu_id}", response_model=dict)
def get_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单详情
    """
    menu = MenuService.get_menu_by_id(db, menu_id)
    if not menu:
        return error_response(code=404, msg="菜单不存在")
    return ResponseModel.success(data=menu)

@router.put("/{menu_id}", response_model=dict)
def update_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    menu_data: Dict[str, Any],
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    更新菜单
    """
    menu = MenuService.get_menu_by_id(db, menu_id)
    if not menu:
        return error_response(code=404, msg="菜单不存在")
    
    menu = MenuService.update_menu(db, menu, menu_data, current_user.username)
    return ResponseModel.success(data=menu)

@router.delete("/{menu_id}", response_model=dict)
def delete_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    删除菜单
    """
    success = MenuService.delete_menu(db, menu_id)
    if not success:
        return error_response(code=404, msg="菜单不存在")
    
    return ResponseModel.success(msg="删除成功") 