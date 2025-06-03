from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Dept(Base):
    __tablename__ = "sys_dept"

    dept_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, default=0)
    ancestors = Column(String(50), default="")
    dept_name = Column(String(30), default="")
    order_num = Column(Integer, default=0)
    leader = Column(String(20), nullable=True)
    phone = Column(String(11), nullable=True)
    email = Column(String(50), nullable=True)
    status = Column(String(1), default="0")
    del_flag = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)

    # 自引用关系
    parent = relationship("Dept", remote_side=[dept_id], backref="children")
    
    # 用户关系
    users = relationship("User", back_populates="dept")

    def __repr__(self):
        return f"<Dept {self.dept_name}>" 