from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DictTypeBase(BaseModel):
    """字典类型基础信息"""
    dict_name: str = Field(..., description="字典名称")
    dict_type: str = Field(..., description="字典类型")
    status: str = Field("0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeCreate(DictTypeBase):
    """创建字典类型"""
    pass


class DictTypeUpdate(DictTypeBase):
    """更新字典类型"""
    dict_id: int = Field(..., description="字典类型ID")


class DictTypeInfo(DictTypeBase):
    """字典类型详细信息"""
    dict_id: int = Field(..., description="字典类型ID")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class DictTypeQuery(BaseModel):
    """字典类型查询参数"""
    dict_name: Optional[str] = Field(None, description="字典名称")
    dict_type: Optional[str] = Field(None, description="字典类型")
    status: Optional[str] = Field(None, description="状态（0正常 1停用）")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100) 