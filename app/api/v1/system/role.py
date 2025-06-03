from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.service.system.role_service import role_service
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleMenuTree
from app.schemas.user import User
from app.utils.response import Response, ResponseModel
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/system/role", tags=["角色管理"])


@router.get("/list", response_model=ResponseModel[dict])
async def get_role_list(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
    role_name: str = Query(None, description="角色名称"),
    role_key: str = Query(None, description="角色标识"),
    status: str = Query(None, description="状态"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取角色列表
    """
    result = role_service.get_role_list(
        db, 
        page=pagination.page_num, 
        page_size=pagination.page_size, 
        role_name=role_name, 
        role_key=role_key, 
        status=status
    )
    return Response.success(result)


@router.get("/{role_id}", response_model=ResponseModel[Role])
async def get_role_detail(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取角色详细信息
    """
    role = role_service.get_role_by_id(db, role_id)
    return Response.success(role)


@router.post("", response_model=ResponseModel[Role])
async def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    创建新角色
    """
    role = role_service.create_role(db, role_in)
    return Response.success(role, msg="角色创建成功")


@router.put("/{role_id}", response_model=ResponseModel[Role])
async def update_role(
    role_in: RoleUpdate,
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新角色信息
    """
    role = role_service.update_role(db, role_id, role_in)
    return Response.success(role, msg="角色更新成功")


@router.delete("/{role_id}", response_model=ResponseModel)
async def delete_role(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    删除角色
    """
    role_service.delete_role(db, role_id)
    return Response.success(msg="角色删除成功")


@router.post("/batch/remove", response_model=ResponseModel)
async def batch_delete_roles(
    role_ids: List[int] = Body(..., description="角色ID列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    批量删除角色
    """
    role_service.batch_delete_roles(db, role_ids)
    return Response.success(msg="角色批量删除成功")


@router.put("/{role_id}/status/{status}", response_model=ResponseModel)
async def update_role_status(
    role_id: int = Path(..., description="角色ID"),
    status: str = Path(..., description="状态", regex="^[01]$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    修改角色状态
    """
    role_service.update_role_status(db, role_id, status)
    return Response.success(msg="角色状态更新成功")


@router.get("/all", response_model=ResponseModel[List[Role]])
async def get_all_roles(
    db: Session = Depends(get_db),
    status: str = Query(None, description="状态"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取所有角色
    """
    roles = role_service.get_all_roles(db, status=status)
    return Response.success(roles)


@router.get("/{role_id}/menu-tree", response_model=ResponseModel[RoleMenuTree])
async def get_role_menu_tree(
    role_id: int = Path(..., description="角色ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取角色菜单权限树
    """
    role_menu_tree = role_service.get_role_menu_tree(db, role_id)
    return Response.success(role_menu_tree) 