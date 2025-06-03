from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, create_model
from pydantic.generics import GenericModel


DataT = TypeVar('DataT')


class ResponseModel(GenericModel, Generic[DataT]):
    """
    统一响应模型
    """
    code: int = Field(200, description="业务状态码")
    msg: str = Field("操作成功", description="提示信息")
    data: Optional[DataT] = Field(None, description="数据")


class Response:
    """
    统一响应工具类
    """
    
    @staticmethod
    def success(
        data: Any = None,
        msg: str = "操作成功",
        code: int = 200
    ) -> Dict[str, Any]:
        """
        成功响应
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def error(
        msg: str = "操作失败",
        code: int = 500,
        data: Any = None
    ) -> Dict[str, Any]:
        """
        错误响应
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def table(
        rows: List[Dict[str, Any]],
        total: int,
        msg: str = "查询成功"
    ) -> Dict[str, Any]:
        """
        表格数据响应
        """
        return {
            "code": 200,
            "msg": msg,
            "rows": rows,
            "total": total
        } 