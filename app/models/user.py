from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class User(Base):
    __tablename__ = "sys_user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dept_id = Column(Integer, ForeignKey("sys_dept.dept_id"), nullable=True)
    username = Column(String(30), unique=True, index=True, nullable=False)
    nickname = Column(String(30), nullable=False)
    user_type = Column(String(2), default="00")
    email = Column(String(50), default="")
    phonenumber = Column(String(11), default="")
    sex = Column(String(1), default="0")
    avatar = Column(String(100), default="")
    password = Column(String(100), default="")
    status = Column(String(1), default="0")
    del_flag = Column(String(1), default="0")
    login_ip = Column(String(128), default="")
    login_date = Column(DateTime, nullable=True)
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), default="")

    # 关系定义
    dept = relationship("Dept", back_populates="users")
    roles = relationship("Role", secondary="sys_user_role", back_populates="users")
    posts = relationship("Post", secondary="sys_user_post", back_populates="users")

    def __repr__(self):
        return f"<User {self.username}>" 