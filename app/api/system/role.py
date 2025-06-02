from typing import List
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.role import RoleCreate, RoleUpdate, RoleInfo, RoleQuery
from app.common.response import success, error, page
from app.service.system.role_service import (
    get_role, get_roles, create_role, update_role, 
    delete_role, update_role_status, get_all_roles,
    get_role_menu_ids, get_role_dept_ids
)

router = APIRouter()


@router.get("/list", summary="获取角色列表")
async def get_role_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: RoleQuery = Depends(),
):
    """
    获取角色列表（分页查询）
    """
    try:
        roles, total = get_roles(db, params)
        # 转换为前端格式
        role_list = [
            {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "role_key": role.role_key,
                "role_sort": role.role_sort,
                "data_scope": role.data_scope,
                "status": role.status,
                "create_time": role.create_time,
                "remark": role.remark
            }
            for role in roles
        ]
        return page(rows=role_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/all", summary="获取所有角色")
async def get_all_role_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取所有角色列表（不分页）
    """
    try:
        roles = get_all_roles(db)
        # 转换为前端格式
        role_list = [
            {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "role_key": role.role_key,
                "role_sort": role.role_sort,
                "data_scope": role.data_scope,
                "status": role.status
            }
            for role in roles
        ]
        return success(data=role_list)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{role_id}", summary="获取角色详情")
async def get_role_info(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取角色详情
    """
    try:
        role = get_role(db, role_id)
        if not role:
            return error(msg="角色不存在", code=404)
        
        # 获取菜单ID列表
        menu_ids = get_role_menu_ids(db, role_id)
        
        # 获取部门ID列表（仅当数据范围为自定数据权限时）
        dept_ids = [] if role.data_scope != "2" else get_role_dept_ids(db, role_id)
        
        # 转换为前端格式
        role_info = {
            "role_id": role.role_id,
            "role_name": role.role_name,
            "role_key": role.role_key,
            "role_sort": role.role_sort,
            "data_scope": role.data_scope,
            "status": role.status,
            "create_time": role.create_time,
            "remark": role.remark,
            "menu_ids": menu_ids,
            "dept_ids": dept_ids
        }
        return success(data=role_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加角色")
async def add_role(
    role_data: RoleCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加角色
    """
    try:
        role = create_role(db, role_data)
        return success(msg="角色添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改角色")
async def edit_role(
    role_data: RoleUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改角色
    """
    try:
        role = update_role(db, role_data.role_id, role_data)
        return success(msg="角色修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{role_id}", summary="删除角色")
async def remove_role(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除角色
    """
    try:
        result = delete_role(db, role_id)
        return success(msg="角色删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.put("/changeStatus", summary="修改角色状态")
async def change_role_status(
    role_id: int = Body(..., embed=True),
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改角色状态
    """
    try:
        role = update_role_status(db, role_id, status)
        return success(msg="角色状态修改成功")
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 