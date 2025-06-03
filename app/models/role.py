from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


# 角色与菜单关联表
role_menu = Table(
    "sys_role_menu",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("sys_menu.menu_id"), primary_key=True)
)

# 角色与部门关联表
role_dept = Table(
    "sys_role_dept",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True),
    Column("dept_id", Integer, ForeignKey("sys_dept.dept_id"), primary_key=True)
)

# 用户与角色关联表
user_role = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True)
)


class Role(Base):
    __tablename__ = "sys_role"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(30), nullable=False)
    role_key = Column(String(100), nullable=False)
    role_sort = Column(Integer, nullable=False)
    data_scope = Column(String(1), default="1")
    status = Column(String(1), nullable=False)
    del_flag = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), nullable=True)

    # 关系定义
    users = relationship("User", secondary=user_role, back_populates="roles")
    menus = relationship("Menu", secondary=role_menu)
    depts = relationship("Dept", secondary=role_dept)

    def __repr__(self):
        return f"<Role {self.role_name}>" 