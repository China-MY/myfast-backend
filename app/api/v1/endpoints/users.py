from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user, get_current_admin_user
from app.entity.sys_user import SysUser
from app.service.system.user_service import UserService
from app.schema.user import UserCreate, UserUpdate, UserInfo, UserQuery, UserUpdatePassword
from app.common.response import ResponseModel, success_response, error_response

router = APIRouter()

@router.get("/", response_model=dict)
def get_users(
    *,
    db: Session = Depends(get_db),
    query: UserQuery,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取用户列表
    """
    users_data = UserService.get_users(
        db, 
        page_num=query.page_num, 
        page_size=query.page_size,
        username=query.username,
        nickname=query.nickname,
        status=query.status,
        dept_id=query.dept_id,
        begin_time=query.begin_time,
        end_time=query.end_time
    )
    
    return ResponseModel.page_response(
        data=[UserInfo.from_orm(user) for user in users_data["items"]],
        total=users_data["total"],
        page_num=users_data["page_num"],
        page_size=users_data["page_size"]
    )

@router.post("/", response_model=dict)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    创建新用户
    """
    user = UserService.create_user(db, user_in, current_user.username)
    return ResponseModel.success(data=UserInfo.from_orm(user))

@router.get("/{user_id}", response_model=dict)
def get_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    获取指定用户信息
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        return error_response(code=404, msg="用户不存在")
    return ResponseModel.success(data=UserInfo.from_orm(user))

@router.put("/{user_id}", response_model=dict)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    更新用户信息
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        return error_response(code=404, msg="用户不存在")
    
    user = UserService.update_user(db, user, user_in, current_user.username)
    return ResponseModel.success(data=UserInfo.from_orm(user))

@router.delete("/{user_id}", response_model=dict)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    删除用户
    """
    if user_id == current_user.user_id:
        return error_response(code=400, msg="不能删除当前登录用户")
    
    success = UserService.delete_user(db, user_id, current_user.username)
    if not success:
        return error_response(code=404, msg="用户不存在")
    
    return ResponseModel.success(msg="删除成功")

@router.put("/{user_id}/password", response_model=dict)
def update_password(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    password_data: UserUpdatePassword,
    current_user: SysUser = Depends(get_current_active_user),
) -> Any:
    """
    修改用户密码
    """
    # 只允许管理员或用户本人修改密码
    if current_user.user_id != user_id:
        admin_roles = [role for role in current_user.roles if role.role_key == "admin"]
        if not admin_roles:
            return error_response(code=403, msg="无权限修改他人密码")
    
    # 验证新密码与确认密码是否一致
    if password_data.new_password != password_data.confirm_password:
        return error_response(code=400, msg="新密码与确认密码不一致")
    
    # 如果是用户本人修改密码，需要验证旧密码
    if current_user.user_id == user_id:
        if not UserService.authenticate_user(db, current_user.username, password_data.old_password):
            return error_response(code=400, msg="旧密码错误")
    
    success = UserService.update_user_password(
        db, user_id, password_data.new_password, current_user.username
    )
    if not success:
        return error_response(code=404, msg="用户不存在")
    
    return ResponseModel.success(msg="密码修改成功")

@router.put("/{user_id}/status", response_model=dict)
def update_status(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    status: str,
    current_user: SysUser = Depends(get_current_admin_user),
) -> Any:
    """
    修改用户状态
    """
    if user_id == current_user.user_id:
        return error_response(code=400, msg="不能修改当前登录用户状态")
    
    success = UserService.update_user_status(db, user_id, status, current_user.username)
    if not success:
        return error_response(code=404, msg="用户不存在")
    
    return ResponseModel.success(msg="状态修改成功") 