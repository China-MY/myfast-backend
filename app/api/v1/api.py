from fastapi import APIRouter

from app.api.v1.auth import login, register
from app.api.v1.system import user, profile

# 创建API路由器
api_router = APIRouter()

# 认证相关路由
api_router.include_router(login.router, prefix="/auth", tags=["认证"])
api_router.include_router(register.router, prefix="/auth/register", tags=["注册"])

# 系统管理路由
api_router.include_router(user.router, prefix="/system/user", tags=["用户管理"])
api_router.include_router(profile.router, prefix="/system/user/profile", tags=["用户信息"]) 