import logging
from typing import Callable

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# 配置日志
logger = logging.getLogger("app")


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    异常处理中间件
    统一处理各种异常，并返回标准的JSON响应
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # 处理请求
            return await call_next(request)
        except HTTPException as exc:
            # 处理FastAPI的HTTP异常
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "code": exc.status_code,
                    "msg": exc.detail,
                    "data": None
                }
            )
        except Exception as exc:
            # 处理未捕获的异常
            logger.exception(f"Unhandled exception: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "msg": "服务器内部错误",
                    "data": None
                }
            ) 