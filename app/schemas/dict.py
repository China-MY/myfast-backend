from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# 字典类型模型
class DictTypeBase(BaseModel):
    """字典类型基本属性"""
    dict_name: Optional[str] = None
    dict_type: Optional[str] = None
    status: Optional[str] = "0"
    remark: Optional[str] = None


class DictTypeCreate(DictTypeBase):
    """创建字典类型模型"""
    dict_name: str
    dict_type: str


class DictTypeUpdate(DictTypeBase):
    """更新字典类型模型"""
    pass


class DictTypeInDB(DictTypeBase):
    """数据库字典类型模型"""
    dict_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DictTypeOut(DictTypeInDB):
    """字典类型输出模型"""
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# 字典数据模型
class DictDataBase(BaseModel):
    """字典数据基本属性"""
    dict_sort: Optional[int] = 0
    dict_label: Optional[str] = None
    dict_value: Optional[str] = None
    dict_type: Optional[str] = None
    css_class: Optional[str] = None
    list_class: Optional[str] = None
    is_default: Optional[str] = "N"
    status: Optional[str] = "0"
    remark: Optional[str] = None


class DictDataCreate(DictDataBase):
    """创建字典数据模型"""
    dict_label: str
    dict_value: str
    dict_type: str


class DictDataUpdate(DictDataBase):
    """更新字典数据模型"""
    pass


class DictDataInDB(DictDataBase):
    """数据库字典数据模型"""
    dict_code: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DictDataOut(DictDataInDB):
    """字典数据输出模型"""
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) 