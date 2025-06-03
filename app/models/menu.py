from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Menu(Base):
    __tablename__ = "sys_menu"

    menu_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_name = Column(String(50), nullable=False)
    parent_id = Column(Integer, default=0)
    order_num = Column(Integer, default=0)
    path = Column(String(200), default="")
    component = Column(String(255), nullable=True)
    query = Column(String(255), nullable=True)
    is_frame = Column(Integer, default=1)
    is_cache = Column(Integer, default=0)
    menu_type = Column(String(1), default="")
    visible = Column(String(1), default="0")
    status = Column(String(1), default="0")
    perms = Column(String(100), nullable=True)
    icon = Column(String(100), default="#")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), default="")

    # 自引用关系
    parent = relationship("Menu", remote_side=[menu_id], backref="children")

    def __repr__(self):
        return f"<Menu {self.menu_name}>" 