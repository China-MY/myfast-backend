from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.user import user as user_crud
from app.schemas.token import Token
from app.schemas.user import User, UserLogin, UserPermissions
from app.core.config import settings
from app.core.security import create_access_token
from app.utils.response import Response, ResponseModel

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login", response_model=ResponseModel[Token])
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的令牌登录，获取访问令牌
    """
    user = user_crud.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "0":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.user_id, 
        expires_delta=access_token_expires
    )
    
    # 返回令牌
    return Response.success({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    })


@router.post("/login/account", response_model=ResponseModel[Token])
async def login_by_account(
    user_in: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户账号密码登录
    """
    # 验证用户
    user = user_crud.authenticate(db, username=user_in.username, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    if user.status != "0":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.user_id, 
        expires_delta=access_token_expires
    )
    
    # 返回令牌
    return Response.success({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    })


@router.post("/logout", response_model=ResponseModel)
async def logout(current_user: User = Depends(get_current_user)) -> Any:
    """
    用户登出
    """
    # 前端清除令牌即可，后端无需特殊处理
    return Response.success(msg="登出成功")


@router.get("/info", response_model=ResponseModel[UserPermissions])
async def get_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息
    """
    # 获取用户角色
    roles = []
    db_roles = user_crud.get_user_roles(db, current_user.user_id)
    for role in db_roles:
        roles.append({
            "role_id": role.role_id,
            "role_name": role.role_name,
            "role_key": role.role_key
        })
    
    # 获取权限集合
    permissions = []
    for role in roles:
        # 这里应该调用权限服务获取角色对应的权限,简化处理
        if role["role_key"] == "admin":
            permissions.append("*:*:*")  # 管理员拥有所有权限
    
    # 构建用户信息
    user_info = UserPermissions(
        user_id=current_user.user_id,
        username=current_user.username,
        nickname=current_user.nickname,
        roles=roles,
        permissions=permissions
    )
    
    return Response.success(user_info) 