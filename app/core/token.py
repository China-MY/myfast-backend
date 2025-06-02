from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """JWT令牌载荷"""
    sub: Optional[int] = None  # 用户ID
    exp: Optional[datetime] = None  # 过期时间 