from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# 字典类型模型
class DictTypeBase(BaseModel):
    """字典类型基础模型"""
    dict_name: str = Field(..., description="字典名称")
    dict_type: str = Field(..., description="字典类型")
    status: str = Field("0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeCreate(DictTypeBase):
    """字典类型创建模型"""
    pass


class DictTypeUpdate(BaseModel):
    """字典类型更新模型"""
    dict_name: Optional[str] = Field(None, description="字典名称")
    dict_type: Optional[str] = Field(None, description="字典类型")
    status: Optional[str] = Field(None, description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeInDBBase(DictTypeBase):
    """字典类型数据库模型"""
    dict_id: int = Field(..., description="字典主键")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: datetime = Field(..., description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class DictTypeOut(DictTypeInDBBase):
    """字典类型输出模型"""
    pass


class DictTypeWithCountOut(DictTypeOut):
    """带字典数据计数的字典类型输出模型"""
    dict_data_count: int = Field(0, description="字典数据数量")


# 字典数据模型
class DictDataBase(BaseModel):
    """字典数据基础模型"""
    dict_sort: int = Field(0, description="字典排序")
    dict_label: str = Field(..., description="字典标签")
    dict_value: str = Field(..., description="字典键值")
    dict_type: str = Field(..., description="字典类型")
    css_class: Optional[str] = Field(None, description="样式属性")
    list_class: Optional[str] = Field(None, description="表格回显样式")
    is_default: str = Field("N", description="是否默认（Y是 N否）")
    status: str = Field("0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictDataCreate(DictDataBase):
    """字典数据创建模型"""
    pass


class DictDataUpdate(BaseModel):
    """字典数据更新模型"""
    dict_sort: Optional[int] = Field(None, description="字典排序")
    dict_label: Optional[str] = Field(None, description="字典标签")
    dict_value: Optional[str] = Field(None, description="字典键值")
    dict_type: Optional[str] = Field(None, description="字典类型")
    css_class: Optional[str] = Field(None, description="样式属性")
    list_class: Optional[str] = Field(None, description="表格回显样式")
    is_default: Optional[str] = Field(None, description="是否默认（Y是 N否）")
    status: Optional[str] = Field(None, description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class DictDataInDBBase(DictDataBase):
    """字典数据数据库模型"""
    dict_code: int = Field(..., description="字典编码")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: datetime = Field(..., description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class DictDataOut(DictDataInDBBase):
    """字典数据输出模型"""
    pass


# 字典数据选项模型
class DictDataOption(BaseModel):
    """字典数据选项模型，用于前端下拉框"""
    value: str = Field(..., description="字典键值")
    label: str = Field(..., description="字典标签")
    class_name: Optional[str] = Field(None, description="样式类名")
    is_default: str = Field("N", description="是否默认")


# 辅助函数
def dict_type_to_dict(dict_type):
    """将SysDictType模型转换为字典"""
    if not dict_type:
        return None
    
    return {
        "dict_id": dict_type.dict_id,
        "dict_name": dict_type.dict_name,
        "dict_type": dict_type.dict_type,
        "status": dict_type.status,
        "create_by": dict_type.create_by,
        "create_time": dict_type.create_time,
        "update_by": dict_type.update_by,
        "update_time": dict_type.update_time,
        "remark": dict_type.remark
    }


def dict_data_to_dict(dict_data):
    """将SysDictData模型转换为字典"""
    if not dict_data:
        return None
    
    return {
        "dict_code": dict_data.dict_code,
        "dict_sort": dict_data.dict_sort,
        "dict_label": dict_data.dict_label,
        "dict_value": dict_data.dict_value,
        "dict_type": dict_data.dict_type,
        "css_class": dict_data.css_class,
        "list_class": dict_data.list_class,
        "is_default": dict_data.is_default,
        "status": dict_data.status,
        "create_by": dict_data.create_by,
        "create_time": dict_data.create_time,
        "update_by": dict_data.update_by,
        "update_time": dict_data.update_time,
        "remark": dict_data.remark
    } 