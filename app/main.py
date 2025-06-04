import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI企业级后台权限管理系统",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
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