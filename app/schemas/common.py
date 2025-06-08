from typing import Any, Generic, Optional, TypeVar, Dict, List

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ResponseModel(BaseModel, Generic[DataT]):
    """通用响应模型"""
    code: int = Field(default=200, description="响应状态码：200成功，其他为失败")
    msg: str = Field(default="操作成功", description="响应消息")
    data: Optional[DataT] = Field(default=None, description="响应数据")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200, 
                "msg": "操作成功", 
                "data": None
            }
        }
    )


class PageInfo(BaseModel):
    """分页信息"""
    page: int = Field(default=1, description="当前页码", ge=1)
    pageSize: int = Field(default=10, description="每页大小", ge=1, le=100)
    total: int = Field(default=0, description="总条数", ge=0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "pageSize": 10,
                "total": 100
            }
        }
    )


class PageResponseModel(BaseModel, Generic[DataT]):
    """分页响应模型"""
    code: int = Field(default=200, description="响应状态码：200成功，其他为失败")
    msg: str = Field(default="操作成功", description="响应消息")
    rows: List[DataT] = Field(default_factory=list, description="数据列表")
    pageInfo: PageInfo = Field(default_factory=PageInfo, description="分页信息")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "msg": "操作成功",
                "rows": [],
                "pageInfo": {
                    "page": 1,
                    "pageSize": 10,
                    "total": 100
                }
            }
        }
    ) 