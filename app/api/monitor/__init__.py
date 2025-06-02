from fastapi import APIRouter

from app.api.monitor.online import router as online_router
from app.api.monitor.job import router as job_router
from app.api.monitor.server import router as server_router
from app.api.monitor.cache import router as cache_router

# 创建系统监控路由
monitor_router = APIRouter()

# 注册子路由
monitor_router.include_router(online_router, prefix="/online", tags=["在线用户"])
monitor_router.include_router(job_router, prefix="/job", tags=["定时任务"])
monitor_router.include_router(server_router, prefix="/server", tags=["服务监控"])
monitor_router.include_router(cache_router, prefix="/cache", tags=["缓存监控"]) 