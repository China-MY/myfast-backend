from fastapi import APIRouter

from app.api.auth.login import router as login_router

# 创建认证路由
auth_router = APIRouter()

# 注册子路由
auth_router.include_router(login_router, tags=["用户认证"]) 