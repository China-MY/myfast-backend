from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码上下文，用于哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建访问令牌
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
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
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # 输出调试信息
    print(f"[DEBUG] 创建访问令牌: subject={subject}, expires={expire}")
    
    return encoded_jwt

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码哈希
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.system.user import SysUser
from app.schemas.utils.token import TokenPayload
from app.crud.system.user import user as crud_user

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> SysUser:
    """
    验证并获取当前用户
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = crud_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.status != "0":  # 0表示正常状态
        raise HTTPException(status_code=400, detail="用户被禁用")
    return user


def get_current_active_user(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """
    获取当前活跃用户
    """
    if current_user.status != "0":
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

def get_current_user_id(current_user: SysUser = Depends(get_current_active_user)) -> int:
    """获取当前用户ID"""
    return current_user.user_id 