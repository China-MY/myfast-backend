from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.session import Base

# 用户和角色关联表
SysUserRole = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True, comment="用户ID"),
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID")
)

# 用户和岗位关联表  
SysUserPost = Table(
    "sys_user_post",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True, comment="用户ID"),
    Column("post_id", Integer, ForeignKey("sys_post.post_id"), primary_key=True, comment="岗位ID")
)

# 角色和菜单关联表
SysRoleMenu = Table(
    "sys_role_menu",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID"),
    Column("menu_id", Integer, ForeignKey("sys_menu.menu_id"), primary_key=True, comment="菜单ID")
)

# 角色和部门关联表
SysRoleDept = Table(
    "sys_role_dept",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.role_id"), primary_key=True, comment="角色ID"),
    Column("dept_id", Integer, ForeignKey("sys_dept.dept_id"), primary_key=True, comment="部门ID")
) 