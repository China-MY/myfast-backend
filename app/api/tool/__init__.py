from fastapi import APIRouter

# 暂时注释掉代码生成相关的导入以避免错误
# from app.api.tool.gen import router as gen_router
from app.api.tool.swagger import router as swagger_router
from app.api.tool.form import router as form_router

# 创建系统工具路由
tool_router = APIRouter()

# 注册子路由
# tool_router.include_router(gen_router, prefix="/gen", tags=["代码生成"])
tool_router.include_router(swagger_router, prefix="/swagger", tags=["系统接口"])
tool_router.include_router(form_router, prefix="/form", tags=["表单构建"]) 