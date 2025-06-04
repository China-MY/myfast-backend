from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user, get_current_admin_user
from app.entity.sys_user import SysUser
from app.service.system.role_service import RoleService
from app.schema.role import RoleCreate, RoleUpdate, RoleInfo, RoleQuery
from app.common.response import ResponseModel, success_response, error_response

router = APIRouter()

@router.get("/", response_model=dict)
def get_roles(
    *,
    db: Session = Depends(get_db),
    query: RoleQuery,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取角色列表
    """
    roles_data = RoleService.get_roles(
        db, 
        page_num=query.page_num, 
        page_size=query.page_size,
        role_name=query.role_name,
        role_key=query.role_key,
        status=query.status,
        begin_time=query.begin_time,
        end_time=query.end_time
    )
    
    return ResponseModel.page_response(
        data=[RoleInfo.from_orm(role) for role in roles_data["items"]],
        total=roles_data["total"],
        page_num=roles_data["page_num"],
        page_size=roles_data["page_size"]
    )

@router.post("/", response_model=dict)
def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    创建新角色
    """
    role = RoleService.create_role(db, role_in, current_user.username)
    return ResponseModel.success(data=RoleInfo.from_orm(role))

@router.get("/{role_id}", response_model=dict)
def get_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取指定角色信息
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        return error_response(code=404, msg="角色不存在")
    
    # 获取角色关联的菜单ID列表
    menu_ids = RoleService.get_role_menu_ids(db, role_id)
    
    # 获取角色关联的部门ID列表
    dept_ids = RoleService.get_role_dept_ids(db, role_id)
    
    # 构建响应数据
    role_info = RoleInfo.from_orm(role)
    role_info.menu_ids = menu_ids
    role_info.dept_ids = dept_ids
    
    return ResponseModel.success(data=role_info)

@router.put("/{role_id}", response_model=dict)
def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: RoleUpdate,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    更新角色信息
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        return error_response(code=404, msg="角色不存在")
    
    # 不允许修改管理员角色
    if role.role_key == "admin":
        return error_response(code=400, msg="不允许修改管理员角色")
    
    role = RoleService.update_role(db, role, role_in, current_user.username)
    return ResponseModel.success(data=RoleInfo.from_orm(role))

@router.delete("/{role_id}", response_model=dict)
def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    删除角色
    """
    success = RoleService.delete_role(db, role_id, current_user.username)
    if not success:
        return error_response(code=404, msg="角色不存在")
    
    return ResponseModel.success(msg="删除成功")

@router.put("/{role_id}/status", response_model=dict)
def update_status(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    status: str,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    修改角色状态
    """
    success = RoleService.update_role_status(db, role_id, status, current_user.username)
    if not success:
        return error_response(code=404, msg="角色不存在")
    
    return ResponseModel.success(msg="状态修改成功") 