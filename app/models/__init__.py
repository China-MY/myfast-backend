# 导入所有模型以确保SQLAlchemy能够正确初始化关系
# 首先导入关系表定义，避免循环导入
from app.models.utils.relation import SysUserRole, SysUserPost, SysRoleMenu, SysRoleDept

# 再导入实体表
from app.models.system.user import SysUser
from app.models.system.dept import SysDept
from app.models.system.role import SysRole
from app.models.system.post import SysPost
from app.models.system.menu import SysMenu

# 导入所有模型到此命名空间，方便其他模块导入
__all__ = [
    'SysUserRole', 'SysUserPost', 'SysRoleMenu', 'SysRoleDept',
    'SysUser', 'SysDept', 'SysRole', 'SysPost', 'SysMenu'
] 