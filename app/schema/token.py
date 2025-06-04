from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """令牌数据模型"""
    access_token: str
    token_type: str = "bearer"
    
class TokenPayload(BaseModel):
    """令牌载荷数据模型"""
    sub: Optional[str] = None
    exp: Optional[int] = None

class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = None 