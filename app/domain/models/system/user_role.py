from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base


# 用户和角色关联表
SysUserRole = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True, comment="用户ID"),
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID"),
) 