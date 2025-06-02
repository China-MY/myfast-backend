from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ConfigBase(BaseModel):
    """参数配置基础信息"""
    config_name: str = Field(..., description="参数名称")
    config_key: str = Field(..., description="参数键名")
    config_value: str = Field(..., description="参数键值")
    config_type: str = Field("N", description="系统内置（Y是 N否）")
    remark: Optional[str] = Field(None, description="备注")


class ConfigCreate(ConfigBase):
    """创建参数配置"""
    pass


class ConfigUpdate(ConfigBase):
    """更新参数配置"""
    config_id: int = Field(..., description="参数ID")


class ConfigInfo(ConfigBase):
    """参数配置详细信息"""
    config_id: int = Field(..., description="参数ID")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class ConfigQuery(BaseModel):
    """参数配置查询参数"""
    config_name: Optional[str] = Field(None, description="参数名称")
    config_key: Optional[str] = Field(None, description="参数键名")
    config_type: Optional[str] = Field(None, description="系统内置（Y是 N否）")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100) 