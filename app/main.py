import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.tool.gen import GenTable, GenTableColumn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义lifespan上下文管理器来处理启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件：在应用启动时执行
    try:
        # 创建代码生成相关表
        logger.info("检查并创建代码生成表结构...")
        GenTable.__table__.create(engine, checkfirst=True)
        GenTableColumn.__table__.create(engine, checkfirst=True)
        logger.info("代码生成表结构检查完成")
    except Exception as e:
        logger.error(f"创建代码生成表结构失败: {e}")
    
    yield  # 这里会暂停，直到应用关闭
    
    # 关闭事件：在应用关闭时执行
    logger.info("应用正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI企业级后台权限管理系统",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # 使用定义的lifespan上下文管理器
)

# 配置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 挂载API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["首页"])
def root():
    """
    根路由，返回系统信息
    """
    return {
        "message": f"欢迎使用{settings.PROJECT_NAME}后台管理系统API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查接口
@app.get("/health", tags=["系统"])
def health_check():
    """
    健康检查接口
    """
    return {"status": "ok", "message": "系统运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)