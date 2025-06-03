from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    sex: Optional[str] = "0"
    dept_id: Optional[int] = None
    remark: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str
    nickname: str


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserInDB(UserBase):
    """数据库中的用户"""
    user_id: int
    status: str
    del_flag: str
    avatar: Optional[str] = None
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(BaseModel):
    """返回给前端的用户信息"""
    user_id: int
    username: str
    nickname: str
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    sex: str
    avatar: Optional[str] = None
    status: str
    dept_id: Optional[int] = None
    roles: list = []
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: Optional[int] = None 