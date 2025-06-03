from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.service.system.user_service import user_service
from app.schemas.user import User, UserCreate, UserUpdate, ResetPassword, UserPermissions
from app.utils.response import Response, ResponseModel
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/system/user", tags=["用户管理"])


@router.get("/list", response_model=ResponseModel[dict])
async def get_user_list(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
    username: str = Query(None, description="用户名"),
    status: str = Query(None, description="状态"),
    phonenumber: str = Query(None, description="手机号"),
    dept_id: int = Query(None, description="部门ID"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户列表
    """
    result = user_service.get_user_list(
        db, 
        page=pagination.page_num, 
        page_size=pagination.page_size, 
        username=username, 
        status=status, 
        phonenumber=phonenumber, 
        dept_id=dept_id
    )
    return Response.success(result)


@router.get("/{user_id}", response_model=ResponseModel[User])
async def get_user_detail(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户详细信息
    """
    user = user_service.get_user_by_id(db, user_id)
    return Response.success(user)


@router.post("", response_model=ResponseModel[User])
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    创建新用户
    """
    user = user_service.create_user(db, user_in)
    return Response.success(user, msg="用户创建成功")


@router.put("/{user_id}", response_model=ResponseModel[User])
async def update_user(
    user_in: UserUpdate,
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新用户信息
    """
    user = user_service.update_user(db, user_id, user_in)
    return Response.success(user, msg="用户更新成功")


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    删除用户
    """
    user_service.delete_user(db, user_id)
    return Response.success(msg="用户删除成功")


@router.delete("/batch", response_model=ResponseModel)
async def batch_delete_users(
    user_ids: List[int] = Body(..., description="用户ID列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    批量删除用户
    """
    user_service.batch_delete_users(db, user_ids)
    return Response.success(msg="用户批量删除成功")


@router.put("/{user_id}/reset-password", response_model=ResponseModel)
async def reset_user_password(
    password: str = Body(..., embed=True, description="新密码"),
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    重置用户密码
    """
    user_service.reset_password(db, user_id, password)
    return Response.success(msg="密码重置成功")


@router.put("/profile/update-password", response_model=ResponseModel)
async def update_own_password(
    passwords: ResetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    修改当前用户密码
    """
    user_service.update_password(db, current_user.user_id, passwords.old_password, passwords.new_password)
    return Response.success(msg="密码修改成功")


@router.put("/{user_id}/status/{status}", response_model=ResponseModel)
async def update_user_status(
    user_id: int = Path(..., description="用户ID"),
    status: str = Path(..., description="状态", regex="^[01]$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    修改用户状态
    """
    user_service.update_user_status(db, user_id, status)
    return Response.success(msg="用户状态更新成功")


@router.get("/{user_id}/roles", response_model=ResponseModel[List[dict]])
async def get_user_roles(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户角色
    """
    roles = user_service.get_user_roles(db, user_id)
    return Response.success(roles)


@router.get("/{user_id}/posts", response_model=ResponseModel[List[dict]])
async def get_user_posts(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户岗位
    """
    posts = user_service.get_user_posts(db, user_id)
    return Response.success(posts)


@router.get("/profile", response_model=ResponseModel[UserPermissions])
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息及权限
    """
    # 获取用户角色
    roles = user_service.get_user_roles(db, current_user.user_id)
    
    # 获取权限集合
    permissions = []
    for role in roles:
        # 这里应该调用权限服务获取角色对应的权限,简化处理
        if role["role_key"] == "admin":
            permissions.append("*:*:*")  # 管理员拥有所有权限
    
    # 构建用户权限信息
    user_info = UserPermissions(
        user_id=current_user.user_id,
        username=current_user.username,
        nickname=current_user.nickname,
        roles=roles,
        permissions=permissions
    )
    
    return Response.success(user_info) 