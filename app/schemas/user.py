from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# 用户基础模式
class UserBase(BaseModel):
    username: str
    nickname: str
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    sex: Optional[str] = "0"
    status: Optional[str] = "0"
    dept_id: Optional[int] = None
    remark: Optional[str] = None


# 创建用户
class UserCreate(UserBase):
    password: str
    post_ids: Optional[List[int]] = None
    role_ids: Optional[List[int]] = None


# 更新用户
class UserUpdate(UserBase):
    password: Optional[str] = None
    post_ids: Optional[List[int]] = None
    role_ids: Optional[List[int]] = None


# 用户信息
class User(UserBase):
    user_id: int
    avatar: Optional[str] = None
    login_ip: Optional[str] = None
    login_date: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    dept_name: Optional[str] = None
    roles: Optional[List[dict]] = None
    posts: Optional[List[dict]] = None

    class Config:
        orm_mode = True


# 用户登录信息
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captcha: Optional[str] = Field(None, description="验证码")
    captcha_id: Optional[str] = Field(None, description="验证码ID")


# 密码重置
class ResetPassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


# 用户权限信息
class UserPermissions(BaseModel):
    user_id: int
    username: str
    nickname: str
    roles: List[dict]
    permissions: List[str] 