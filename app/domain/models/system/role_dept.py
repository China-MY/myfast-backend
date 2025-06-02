from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base


# 角色和部门关联表
SysRoleDept = Table(
    "sys_role_dept",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID"),
    Column("dept_id", Integer, ForeignKey("sys_dept.dept_id"), primary_key=True, comment="部门ID"),
) 