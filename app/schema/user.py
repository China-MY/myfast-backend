from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# 角色基础模型
class RoleBase(BaseModel):
    role_id: int
    role_name: str
    role_key: str

# 返回用户信息的基础模型
class UserBase(BaseModel):
    user_id: int
    username: str
    nickname: str
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    sex: str
    avatar: Optional[str] = None
    status: str
    dept_id: Optional[int] = None
    
    model_config = {"from_attributes": True}

# 创建用户的请求模型
class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    sex: str = "0"
    status: str = "0"
    dept_id: Optional[int] = None
    role_ids: List[int] = []
    post_ids: List[int] = []
    remark: Optional[str] = None

# 更新用户的请求模型
class UserUpdate(BaseModel):
    user_id: int
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    sex: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None
    dept_id: Optional[int] = None
    role_ids: Optional[List[int]] = None
    post_ids: Optional[List[int]] = None
    remark: Optional[str] = None

# 更新用户密码的请求模型
class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

# 登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str
    code: Optional[str] = None
    uuid: Optional[str] = None

# 用户详细信息响应模型
class UserInfo(UserBase):
    dept_name: Optional[str] = None
    roles: List[RoleBase] = []
    create_time: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# 用户分页查询请求模型
class UserQuery(BaseModel):
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页显示条数")
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    status: Optional[str] = Field(None, description="状态")
    dept_id: Optional[int] = Field(None, description="部门ID")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间") 