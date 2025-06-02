from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DictDataBase(BaseModel):
    """字典数据基础信息"""
    dict_sort: int = Field(0, description="字典排序")
    dict_label: str = Field(..., description="字典标签")
    dict_value: str = Field(..., description="字典键值")
    dict_type: str = Field(..., description="字典类型")
    css_class: Optional[str] = Field(None, description="样式属性（其他样式扩展）")
    list_class: Optional[str] = Field(None, description="表格回显样式")
    is_default: str = Field("N", description="是否默认（Y是 N否）")
    status: str = Field("0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictDataCreate(DictDataBase):
    """创建字典数据"""
    pass


class DictDataUpdate(DictDataBase):
    """更新字典数据"""
    dict_code: int = Field(..., description="字典编码")


class DictDataInfo(DictDataBase):
    """字典数据详细信息"""
    dict_code: int = Field(..., description="字典编码")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class DictDataQuery(BaseModel):
    """字典数据查询参数"""
    dict_type: Optional[str] = Field(None, description="字典类型")
    dict_label: Optional[str] = Field(None, description="字典标签")
    status: Optional[str] = Field(None, description="状态（0正常 1停用）")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100) 