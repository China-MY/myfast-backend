from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class OnlineUserBase(BaseModel):
    """在线用户基础模型"""
    token_id: str = Field(..., description="用户token")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户账号")
    dept_name: Optional[str] = Field("", description="部门名称")
    login_ip: Optional[str] = Field("", description="登录IP地址")
    login_location: Optional[str] = Field("", description="登录地点")
    browser: Optional[str] = Field("", description="浏览器类型")
    os: Optional[str] = Field("", description="操作系统")
    login_time: datetime = Field(..., description="登录时间")
    last_access_time: datetime = Field(..., description="最后访问时间")
    expire_time: datetime = Field(..., description="过期时间")

class OnlineUserCreate(OnlineUserBase):
    """创建在线用户记录"""
    pass

class OnlineUserUpdate(OnlineUserBase):
    """更新在线用户记录"""
    id: int = Field(..., description="会话编号")

class OnlineUserInfo(OnlineUserBase):
    """在线用户信息"""
    id: int = Field(..., description="会话编号")
    
    class Config:
        from_attributes = True

class OnlineUserQuery(BaseModel):
    """在线用户查询参数"""
    username: Optional[str] = Field(None, description="用户账号")
    ip_address: Optional[str] = Field(None, description="登录IP地址")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数") 