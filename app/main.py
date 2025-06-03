from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.system import user, role, menu, dept, post, dict_type, config
from app.api.v1.monitor import online, job, server, cache
from app.api.v1.tool import gen, swagger, build
from app.core.config import settings
from app.db.init_db import init_db
from app.middleware.logging import LoggingMiddleware
from app.middleware.exception import ExceptionMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionMiddleware)

# 注册路由
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(role.router, prefix=settings.API_V1_STR)
app.include_router(menu.router, prefix=settings.API_V1_STR)
app.include_router(dept.router, prefix=settings.API_V1_STR)
app.include_router(post.router, prefix=settings.API_V1_STR)
app.include_router(dict_type.router, prefix=settings.API_V1_STR)
app.include_router(config.router, prefix=settings.API_V1_STR)
app.include_router(online.router, prefix=settings.API_V1_STR)
app.include_router(job.router, prefix=settings.API_V1_STR)
app.include_router(server.router, prefix=settings.API_V1_STR)
app.include_router(cache.router, prefix=settings.API_V1_STR)
app.include_router(gen.router, prefix=settings.API_V1_STR)
app.include_router(swagger.router, prefix=settings.API_V1_STR)
app.include_router(build.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to MyFast API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)