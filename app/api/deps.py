from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import oauth2_scheme, get_current_user as security_get_current_user
from app.models.user import User
from app.schemas.token import TokenPayload


async def get_db() -> Generator:
    """
    获取数据库会话依赖项
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户依赖项
    """
    return await security_get_current_user(db=db, token=token)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户依赖项
    """
    if current_user.status != "0":
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员用户依赖项
    """
    # 通过角色表判断用户是否为管理员
    admin_role = False
    for role in current_user.roles:
        if role.role_key == "admin":
            admin_role = True
            break
    
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    return current_user 