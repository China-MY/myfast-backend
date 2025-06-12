from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.db.base_class import Base


class SysUserOnline(Base):
    """在线用户记录"""
    __tablename__ = "sys_user_online"
    
    sessionId = Column(String(50), primary_key=True, default="", comment="用户会话id")
    user_id = Column(Integer, nullable=True, comment="用户ID")
    user_name = Column(String(50), default="", comment="用户账号")
    ipaddr = Column(String(128), default="", comment="登录IP地址")
    login_location = Column(String(255), default="", comment="登录地点")
    browser = Column(String(50), default="", comment="浏览器类型")
    os = Column(String(50), default="", comment="操作系统")
    status = Column(String(10), default="", comment="在线状态on_line在线off_line离线")
    start_timestamp = Column(DateTime, nullable=True, comment="session创建时间")
    last_access_time = Column(DateTime, nullable=True, comment="session最后访问时间")
    expire_time = Column(Integer, default=0, comment="超时时间，单位为分钟") 