from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


# 共享属性基类
class UserBase(BaseModel):
    """用户基本属性"""
    username: Optional[str] = Field(None, description="用户账号", example="testuser")
    nickname: Optional[str] = Field(None, description="用户昵称", example="测试用户")
    email: Optional[EmailStr] = Field(None, description="用户邮箱", example="test@example.com")
    phonenumber: Optional[str] = Field(None, description="手机号码", example="13800138000")
    sex: Optional[str] = Field("0", description="用户性别（0男 1女 2未知）", example="0")
    status: Optional[str] = Field("0", description="帐号状态（0正常 1停用）", example="0")


# 创建用户时需要的属性
class UserCreate(UserBase):
    """创建用户模型"""
    username: str = Field(..., description="用户账号", example="newuser")
    nickname: str = Field(..., description="用户昵称", example="新用户")
    password: str = Field(..., description="用户密码", example="password123")
    dept_id: Optional[int] = Field(None, description="部门ID", example=100)
    role_ids: Optional[List[int]] = Field([], description="角色ID列表", example=[2])
    post_ids: Optional[List[int]] = Field([], description="岗位ID列表", example=[4])


# 更新用户时可能更新的属性
class UserUpdate(UserBase):
    """更新用户模型"""
    password: Optional[str] = Field(None, description="用户密码", example="newpassword123")
    dept_id: Optional[int] = Field(None, description="部门ID", example=100)
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表", example=[2])
    post_ids: Optional[List[int]] = Field(None, description="岗位ID列表", example=[4])


# 查询用户时返回的属性
class UserInDB(UserBase):
    """数据库用户模型"""
    user_id: int = Field(..., description="用户ID", example=1)
    dept_id: Optional[int] = Field(None, description="部门ID", example=100)
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


# 部门简要信息
class DeptBrief(BaseModel):
    """部门简要信息"""
    dept_id: int = Field(..., description="部门ID", example=100)
    dept_name: str = Field(..., description="部门名称", example="研发部门")
    
    model_config = ConfigDict(from_attributes=True)


# 角色简要信息
class RoleBrief(BaseModel):
    """角色简要信息"""
    role_id: int = Field(..., description="角色ID", example=2)
    role_name: str = Field(..., description="角色名称", example="普通角色")
    role_key: str = Field(..., description="角色标识", example="common")
    
    model_config = ConfigDict(from_attributes=True)


# API返回的用户模型
class User(UserInDB):
    """返回用户模型"""
    roles: Optional[List[RoleBrief]] = Field([], description="用户角色列表")
    dept: Optional[DeptBrief] = Field(None, description="用户部门")
    
    model_config = ConfigDict(from_attributes=True)


# 用户登录信息
class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名", example="admin")
    password: str = Field(..., description="密码", example="123456")


# 用户信息
class UserInfo(BaseModel):
    """用户信息模型"""
    user: User = Field(..., description="用户信息")
    roles: List[str] = Field([], description="角色标识列表", example=["admin", "common"])
    permissions: List[str] = Field([], description="权限列表", example=["system:user:list", "system:user:query"])
    
    model_config = ConfigDict(from_attributes=True) 