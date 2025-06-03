from typing import Any, List, Dict

from fastapi import APIRouter, Body, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_current_admin_user
from app.service.system.menu_service import menu_service
from app.schemas.menu import Menu, MenuCreate, MenuUpdate
from app.schemas.user import User
from app.utils.response import Response, ResponseModel

router = APIRouter(prefix="/system/menu", tags=["菜单管理"])


@router.get("/list", response_model=ResponseModel[List[Menu]])
async def get_menu_list(
    db: Session = Depends(get_db),
    menu_name: str = Query(None, description="菜单名称"),
    status: str = Query(None, description="状态"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取菜单列表
    """
    result = menu_service.get_menu_list(db, menu_name=menu_name, status=status)
    return Response.success(result)


@router.get("/{menu_id}", response_model=ResponseModel[Menu])
async def get_menu_detail(
    menu_id: int = Path(..., description="菜单ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取菜单详细信息
    """
    menu = menu_service.get_menu_by_id(db, menu_id)
    return Response.success(menu)


@router.post("", response_model=ResponseModel[Menu])
async def create_menu(
    menu_in: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 需要管理员权限
) -> Any:
    """
    创建新菜单
    """
    menu = menu_service.create_menu(db, menu_in)
    return Response.success(menu, msg="菜单创建成功")


@router.put("/{menu_id}", response_model=ResponseModel[Menu])
async def update_menu(
    menu_in: MenuUpdate,
    menu_id: int = Path(..., description="菜单ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 需要管理员权限
) -> Any:
    """
    更新菜单信息
    """
    menu = menu_service.update_menu(db, menu_id, menu_in)
    return Response.success(menu, msg="菜单更新成功")


@router.delete("/{menu_id}", response_model=ResponseModel)
async def delete_menu(
    menu_id: int = Path(..., description="菜单ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 需要管理员权限
) -> Any:
    """
    删除菜单
    """
    menu_service.delete_menu(db, menu_id)
    return Response.success(msg="菜单删除成功")


@router.get("/tree/all", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取菜单树结构
    """
    menu_tree = menu_service.get_menu_permission_tree(db)
    return Response.success(menu_tree)


@router.get("/tree/select", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_menu_tree_select(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取菜单下拉树
    """
    tree_select = menu_service.get_menu_tree_select(db)
    return Response.success(tree_select)


@router.get("/router", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_router_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取路由树
    """
    # 判断用户是否为管理员
    is_admin = False
    for role in current_user.roles:
        if role.role_key == "admin":
            is_admin = True
            break
            
    router_tree = menu_service.get_router_tree(db, user_id=current_user.user_id, is_admin=is_admin)
    return Response.success(router_tree)


@router.get("/role/{role_id}", response_model=ResponseModel[Dict[str, Any]])
async def get_role_menu_tree(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取角色菜单树
    """
    role_menu_tree = menu_service.get_role_menu_tree_select(db, role_id)
    return Response.success(role_menu_tree) 