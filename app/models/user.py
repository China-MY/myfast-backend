from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.relation import SysUserRole, SysUserPost


class SysUser(Base):
    """系统用户表"""
    __tablename__ = "sys_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    dept_id = Column(Integer, ForeignKey("sys_dept.dept_id"), nullable=True, comment="部门ID")
    username = Column(String(30), unique=True, nullable=False, comment="用户账号")
    nickname = Column(String(30), nullable=False, comment="用户昵称")
    user_type = Column(String(2), default="00", comment="用户类型（00系统用户）")
    email = Column(String(50), default="", comment="用户邮箱")
    phonenumber = Column(String(11), default="", comment="手机号码")
    sex = Column(String(1), default="0", comment="用户性别（0男 1女 2未知）")
    avatar = Column(String(100), default="", comment="头像地址")
    password = Column(String(100), default="", comment="密码")
    status = Column(String(1), default="0", comment="帐号状态（0正常 1停用）")
    del_flag = Column(String(1), default="0", comment="删除标志（0代表存在 2代表删除）")
    login_ip = Column(String(128), default="", comment="最后登录IP")
    login_date = Column(DateTime, nullable=True, comment="最后登录时间")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default="", comment="备注")

    # 关系
    dept = relationship("SysDept", back_populates="users")
    roles = relationship("SysRole", secondary=SysUserRole, back_populates="users")
    posts = relationship("SysPost", secondary=SysUserPost, back_populates="users") 