from fastapi import APIRouter

from app.api.system.user import router as user_router
from app.api.system.role import router as role_router
from app.api.system.menu import router as menu_router
from app.api.system.dept import router as dept_router
from app.api.system.post import router as post_router
from app.api.system.dict import router as dict_router
from app.api.system.config import router as config_router

# 创建系统管理路由
system_router = APIRouter()

# 注册子路由
system_router.include_router(user_router, prefix="/user", tags=["用户管理"])
system_router.include_router(role_router, prefix="/role", tags=["角色管理"])
system_router.include_router(menu_router, prefix="/menu", tags=["菜单管理"])
system_router.include_router(dept_router, prefix="/dept", tags=["部门管理"])
system_router.include_router(post_router, prefix="/post", tags=["岗位管理"])
system_router.include_router(dict_router, prefix="/dict", tags=["字典管理"])
system_router.include_router(config_router, prefix="/config", tags=["参数设置"]) 