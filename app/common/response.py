from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar('T')

class CommonResponse(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 200
    msg: str = "操作成功"
    data: Optional[T] = None

class PageInfo(BaseModel, Generic[T]):
    """分页数据响应模型"""
    total: int
    list: List[T]
    page_num: int
    page_size: int

class ResponseModel:
    """响应处理工具类"""
    @staticmethod
    def success(*, data: Any = None, msg: str = "操作成功") -> Dict[str, Any]:
        """成功响应"""
        return {
            "code": 200,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def error(*, code: int = 500, msg: str = "操作失败") -> Dict[str, Any]:
        """错误响应"""
        return {
            "code": code,
            "msg": msg,
            "data": None
        }

    @staticmethod
    def page_response(*, 
                      data: List[Any], 
                      total: int, 
                      page_num: int, 
                      page_size: int) -> Dict[str, Any]:
        """分页数据响应"""
        return {
            "code": 200,
            "msg": "操作成功",
            "data": {
                "total": total,
                "list": data,
                "page_num": page_num,
                "page_size": page_size
            }
        }

def success_response(data: Any = None, msg: str = "操作成功") -> JSONResponse:
    """返回成功的JSON响应"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseModel.success(data=data, msg=msg),
    )

def error_response(code: int = 500, msg: str = "操作失败") -> JSONResponse:
    """返回错误的JSON响应"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 业务码与HTTP状态码分离
        content=ResponseModel.error(code=code, msg=msg),
    ) 