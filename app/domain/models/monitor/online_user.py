from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.database import Base


class SysUserOnline(Base):
    """在线用户记录表"""
    __tablename__ = "sys_user_online"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="会话编号")
    token_id = Column(String(100), nullable=False, comment="用户token")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    username = Column(String(50), nullable=False, comment="用户账号")
    dept_name = Column(String(50), default="", comment="部门名称")
    login_ip = Column(String(128), default="", comment="登录IP地址")
    login_location = Column(String(255), default="", comment="登录地点")
    browser = Column(String(50), default="", comment="浏览器类型")
    os = Column(String(50), default="", comment="操作系统")
    login_time = Column(DateTime, default=func.now(), comment="登录时间")
    last_access_time = Column(DateTime, default=func.now(), comment="最后访问时间")
    expire_time = Column(DateTime, comment="过期时间") 