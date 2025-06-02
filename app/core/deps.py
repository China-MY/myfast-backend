from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.redis import get_redis
from app.domain.models.system.user import SysUser
from app.core.security import settings
from app.core.token import TokenPayload

# OAuth2密码授权方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 获取当前用户
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[SysUser]:
    try:
        # 解析JWT令牌
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户信息
    user = db.query(SysUser).filter(
        SysUser.user_id == token_data.sub,
        SysUser.del_flag == "0"
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户状态
    if user.status != "0":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user

# 获取当前活跃用户
def get_current_active_user(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    # 检查用户状态
    if current_user.status != "0":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user 