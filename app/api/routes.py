from fastapi import APIRouter

from app.api.endpoints import auth

api_router = APIRouter()

# 添加认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 这里可以添加其他路由，比如用户管理、权限等 