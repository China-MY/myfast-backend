from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# 用户基础模型
class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phonenumber: Optional[str] = Field(None, description="手机号码")
    sex: Optional[str] = Field("0", description="性别（0男 1女 2未知）")
    avatar: Optional[str] = Field("", description="头像地址")
    status: Optional[str] = Field("0", description="帐号状态（0正常 1停用）")
    dept_id: Optional[int] = Field(None, description="部门ID")
    remark: Optional[str] = Field("", description="备注")

# 创建用户请求模型
class UserCreate(UserBase):
    password: str = Field(..., description="密码")
    role_ids: List[int] = Field([], description="角色ID列表")
    post_ids: List[int] = Field([], description="岗位ID列表")

# 更新用户请求模型
class UserUpdate(UserBase):
    user_id: int = Field(..., description="用户ID")
    password: Optional[str] = Field(None, description="密码")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    post_ids: Optional[List[int]] = Field(None, description="岗位ID列表")

# 用户查询参数模型
class UserQuery(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="用户昵称")
    status: Optional[str] = Field(None, description="帐号状态")
    dept_id: Optional[int] = Field(None, description="部门ID")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")

# 登录请求模型
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    code: Optional[str] = Field(None, description="验证码")
    uuid: Optional[str] = Field(None, description="唯一标识")

# 登录响应模型
class LoginResponse(BaseModel):
    token: str = Field(..., description="访问令牌")
    expires_in: int = Field(..., description="过期时间")

# 用户信息响应模型
class UserInfo(UserBase):
    user_id: int = Field(..., description="用户ID")
    create_time: datetime = Field(..., description="创建时间")
    dept_name: Optional[str] = Field(None, description="部门名称")
    roles: List[dict] = Field([], description="角色列表")
    posts: List[dict] = Field([], description="岗位列表")
    
    class Config:
        from_attributes = True 