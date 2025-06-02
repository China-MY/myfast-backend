from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.menu import MenuCreate, MenuUpdate, MenuInfo
from app.common.response import success, error
from app.service.system.menu_service import (
    get_menu, get_menus, create_menu, update_menu, delete_menu,
    build_menu_tree, build_menu_tree_select, build_router_tree,
    get_menus_by_user_id
)

router = APIRouter()


@router.get("/list", summary="获取菜单列表")
async def get_menu_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    menu_name: str = Query(None, description="菜单名称"),
    status: str = Query(None, description="菜单状态")
):
    """
    获取菜单列表
    """
    try:
        # 获取所有菜单
        menus = get_menus(db)
        
        # 过滤菜单
        if menu_name or status:
            filtered_menus = []
            for menu in menus:
                if menu_name and menu_name not in menu.menu_name:
                    continue
                if status and menu.status != status:
                    continue
                filtered_menus.append(menu)
            menus = filtered_menus
        
        # 构建菜单树
        menu_tree = build_menu_tree(menus)
        
        return success(data=menu_tree)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{menu_id}", summary="获取菜单详情")
async def get_menu_info(
    menu_id: int = Path(..., description="菜单ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    获取菜单详情
    """
    try:
        menu = get_menu(db, menu_id)
        if not menu:
            return error(msg="菜单不存在", code=404)
        
        # 转换为前端格式
        menu_info = {
            "menu_id": menu.menu_id,
            "parent_id": menu.parent_id,
            "menu_name": menu.menu_name,
            "order_num": menu.order_num,
            "path": menu.path,
            "component": menu.component,
            "query": menu.query,
            "is_frame": menu.is_frame,
            "is_cache": menu.is_cache,
            "menu_type": menu.menu_type,
            "visible": menu.visible,
            "status": menu.status,
            "perms": menu.perms,
            "icon": menu.icon,
            "create_time": menu.create_time,
            "remark": menu.remark
        }
        
        return success(data=menu_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加菜单")
async def add_menu(
    menu_data: MenuCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    添加菜单
    """
    try:
        menu = create_menu(db, menu_data)
        return success(msg="菜单添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改菜单")
async def edit_menu(
    menu_data: MenuUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    修改菜单
    """
    try:
        menu = update_menu(db, menu_data.menu_id, menu_data)
        return success(msg="菜单修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{menu_id}", summary="删除菜单")
async def remove_menu(
    menu_id: int = Path(..., description="菜单ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    删除菜单
    """
    try:
        result = delete_menu(db, menu_id)
        return success(msg="菜单删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.get("/treeselect", summary="获取菜单树选择项")
async def get_menu_tree_select(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    获取菜单树选择项
    """
    try:
        # 获取所有菜单
        menus = get_menus(db)
        
        # 构建菜单树
        tree = build_menu_tree_select(menus)
        
        return success(data=tree)
    except Exception as e:
        return error(msg=str(e))


@router.get("/roleMenuTreeselect/{role_id}", summary="获取角色菜单树选择项")
async def get_role_menu_tree_select(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    获取角色菜单树选择项
    """
    try:
        # 获取所有菜单
        menus = get_menus(db)
        
        # 构建菜单树
        tree = build_menu_tree_select(menus)
        
        # 获取角色菜单ID列表
        checkedKeys = db.execute(
            f"SELECT menu_id FROM sys_role_menu WHERE role_id = {role_id}"
        ).fetchall()
        
        # 提取菜单ID
        menu_ids = [item[0] for item in checkedKeys]
        
        return success(data={
            "menus": tree,
            "checkedKeys": menu_ids
        })
    except Exception as e:
        return error(msg=str(e))


@router.get("/routers", summary="获取路由信息")
async def get_routers(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    获取路由信息
    """
    try:
        # 获取当前用户菜单
        menus = get_menus_by_user_id(db, current_user.user_id)
        
        # 构建路由树
        routers = build_router_tree(menus)
        
        return success(data=routers)
    except Exception as e:
        return error(msg=str(e)) 