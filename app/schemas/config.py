from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ConfigBase(BaseModel):
    """配置基础Schema"""
    config_name: str = Field(..., description="参数名称")
    config_key: str = Field(..., description="参数键名")
    config_value: str = Field(..., description="参数键值")
    config_type: str = Field("N", description="系统内置（Y是 N否）")
    remark: Optional[str] = Field(None, description="备注")


class ConfigCreate(ConfigBase):
    """创建配置的Schema"""
    pass


class ConfigUpdate(ConfigBase):
    """更新配置的Schema"""
    config_name: Optional[str] = Field(None, description="参数名称")
    config_key: Optional[str] = Field(None, description="参数键名")
    config_value: Optional[str] = Field(None, description="参数键值") 
    config_type: Optional[str] = Field(None, description="系统内置（Y是 N否）")


class ConfigInDBBase(ConfigBase):
    """数据库中配置的Schema"""
    config_id: int
    create_by: str
    create_time: datetime
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ConfigOut(ConfigInDBBase):
    """返回的配置Schema"""
    pass


class ConfigPagination(BaseModel):
    """配置分页Schema"""
    rows: List[ConfigOut]
    total: int 