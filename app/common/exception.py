from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.common.response import ResponseModel

class BusinessException(HTTPException):
    """业务异常"""
    def __init__(
        self,
        code: int,
        msg: str = "业务处理异常",
    ) -> None:
        self.code = code
        self.msg = msg
        super().__init__(status_code=200, detail=msg)


async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """业务异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.error(code=exc.code, msg=exc.msg),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求参数验证异常处理器"""
    error_messages = []
    for error in exc.errors():
        loc = " -> ".join([str(x) for x in error["loc"]])
        error_messages.append(f"{loc}: {error['msg']}")
    
    error_message = "；".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.error(code=400, msg=f"参数校验失败: {error_message}"),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.error(code=exc.status_code, msg=exc.detail),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.error(code=500, msg=f"系统异常: {str(exc)}"),
    ) 