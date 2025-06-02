from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base


# 角色和菜单关联表
SysRoleMenu = Table(
    "sys_role_menu",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID"),
    Column("menu_id", Integer, ForeignKey("sys_menu.menu_id"), primary_key=True, comment="菜单ID"),
) 