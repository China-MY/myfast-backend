from fastapi import APIRouter

from app.api.v1.auth import login, register, logout
from app.api.v1.system import user, profile, role, menu, dept, post, dict, config
from app.api.v1.monitor import online, server, job

# 创建API路由器
api_router = APIRouter()

# 认证相关路由
api_router.include_router(login.router, prefix="/auth", tags=["认证"])
api_router.include_router(register.router, prefix="/auth/register", tags=["注册"])
api_router.include_router(logout.router, prefix="/auth", tags=["认证"])

# 系统管理路由
api_router.include_router(user.router, prefix="/system/user", tags=["用户管理"])
api_router.include_router(profile.router, prefix="/system/user/profile", tags=["用户信息"])
api_router.include_router(role.router, prefix="/system/role", tags=["角色管理"])
api_router.include_router(menu.router, prefix="/system/menu", tags=["菜单管理"])
api_router.include_router(dept.router, prefix="/system/dept", tags=["部门管理"])
api_router.include_router(post.router, prefix="/system/post", tags=["岗位管理"])
api_router.include_router(dict.router, prefix="/system/dict", tags=["字典管理"])
api_router.include_router(config.router, prefix="/system/config", tags=["参数设置"])

# 系统监控路由
api_router.include_router(online.router, prefix="/monitor/online", tags=["在线用户"])
api_router.include_router(server.router, prefix="/monitor/server", tags=["服务器监控"])
api_router.include_router(job.router, prefix="/monitor/job", tags=["定时任务"])