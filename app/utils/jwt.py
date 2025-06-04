from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt

from app.core.config import settings


def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None, data: Dict[str, Any] = None
) -> str:
    """
    创建访问令牌
    :param subject: 主题（通常为用户ID）
    :param expires_delta: 过期时间
    :param data: 附加数据
    :return: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    if data:
        to_encode.update(data)
        
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt 