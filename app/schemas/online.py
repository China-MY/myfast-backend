from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class OnlineUserBase(BaseModel):
    """在线用户基础Schema"""
    sessionId: str = Field(..., description="用户会话id")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_name: str = Field("", description="用户账号")
    ipaddr: str = Field("", description="登录IP地址")
    login_location: str = Field("", description="登录地点")
    browser: str = Field("", description="浏览器类型")
    os: str = Field("", description="操作系统")
    status: str = Field("", description="在线状态on_line在线off_line离线")


class OnlineUserCreate(OnlineUserBase):
    """创建在线用户记录的Schema"""
    start_timestamp: Optional[datetime] = Field(None, description="session创建时间")
    last_access_time: Optional[datetime] = Field(None, description="session最后访问时间")
    expire_time: int = Field(0, description="超时时间，单位为分钟")


class OnlineUserInDBBase(OnlineUserBase):
    """数据库中在线用户的Schema"""
    start_timestamp: Optional[datetime] = Field(None, description="session创建时间")
    last_access_time: Optional[datetime] = Field(None, description="session最后访问时间")
    expire_time: int = Field(0, description="超时时间，单位为分钟")
    
    model_config = {"from_attributes": True}


class OnlineUserOut(OnlineUserInDBBase):
    """返回的在线用户Schema"""
    pass


class OnlineUserPagination(BaseModel):
    """在线用户分页Schema"""
    rows: List[OnlineUserOut]
    total: int


class ForceLogoutParams(BaseModel):
    """强制登出参数"""
    session_ids: List[str] = Field(..., description="会话ID列表") 