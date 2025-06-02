from fastapi import APIRouter

from app.api.auth import auth_router
from app.api.system import system_router
from app.api.monitor import monitor_router
from app.api.tool import tool_router

# 创建API路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(system_router, prefix="/system", tags=["系统管理"])
api_router.include_router(monitor_router, prefix="/monitor", tags=["系统监控"])
api_router.include_router(tool_router, prefix="/tool", tags=["系统工具"])