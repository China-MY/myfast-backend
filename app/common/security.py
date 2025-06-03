import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.config.settings import settings


# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 加盐值
SALT = "myfast"


def get_password_hash(password: str) -> str:
    """
    对密码进行md5加盐加密
    
    Args:
        password: 原始密码
        
    Returns:
        加密后的密码
    """
    # 将原始密码与盐值组合
    salted_password = f"{password}{SALT}"
    # 使用md5加密
    md5_hash = hashlib.md5(salted_password.encode()).hexdigest()
    return md5_hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码
        
    Returns:
        验证结果
    """
    # 对明文密码进行相同的加密处理
    hashed_plain_password = get_password_hash(plain_password)
    # 比较加密结果
    return hashed_plain_password == hashed_password


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 令牌主体，通常是用户ID
        expires_delta: 过期时间
        
    Returns:
        JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt 