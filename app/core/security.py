from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload
from app.db.session import get_db

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码Bearer认证流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 创建访问令牌
def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    创建访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码哈希
def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    """
    return pwd_context.hash(password)

async def get_current_user(
    db=Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户
    """
    try:
        # 解码令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # 检查令牌是否过期
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 从数据库获取用户
    user = db.query(User).filter(User.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    
    # 检查用户状态
    if user.status != "0":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用"
        )
        
    return user 