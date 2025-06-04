from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型，通常是bearer")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", 
                "token_type": "bearer"
            }
        }
    )


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: Optional[str] = Field(None, description="用户ID")
    exp: Optional[int] = Field(None, description="过期时间戳")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "1", 
                "exp": 1646756321
            }
        }
    )


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "username": "admin"
            }
        }
    ) 