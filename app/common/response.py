from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class ResponseBase(BaseModel):
    """基础响应模型"""
    code: int = 200
    msg: str = "操作成功"


class Response(ResponseBase):
    """通用响应模型"""
    data: Optional[Any] = None


class PageInfo(BaseModel):
    """分页信息"""
    total: int = 0
    page_num: int = 1
    page_size: int = 10


class PageResult(ResponseBase):
    """分页响应模型"""
    rows: List[Any] = []
    total: int = 0


def success(
    data: Optional[Any] = None, 
    msg: str = "操作成功"
) -> Dict[str, Any]:
    """成功响应"""
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }


def error(
    msg: str = "操作失败", 
    code: int = 500, 
    data: Optional[Any] = None
) -> Dict[str, Any]:
    """错误响应"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


def page(
    rows: List[Any], 
    total: int, 
    msg: str = "查询成功"
) -> Dict[str, Any]:
    """分页响应"""
    return {
        "code": 200,
        "msg": msg,
        "rows": rows,
        "total": total
    } 