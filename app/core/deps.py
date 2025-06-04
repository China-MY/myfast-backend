from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.entity.sys_user import SysUser
from app.schema.token import TokenPayload

# OAuth2密码模式
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# 获取当前用户信息
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> SysUser:
    """
    解析JWT令牌，获取当前用户
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭证",
        )
    user = db.query(SysUser).filter(SysUser.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.status != "0":
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return user

# 获取当前活跃用户
def get_current_active_user(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """
    确保当前用户是活跃状态
    """
    if current_user.status != "0":
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

# 验证是否为管理员用户
def get_current_admin_user(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """
    验证是否为管理员用户
    """
    # 检查用户是否拥有admin角色
    admin_roles = [role for role in current_user.roles if role.role_key == "admin"]
    if not admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    return current_user 