from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PostBase(BaseModel):
    """岗位基础信息"""
    post_name: str = Field(..., description="岗位名称")
    post_code: str = Field(..., description="岗位编码")
    post_sort: int = Field(0, description="岗位排序")
    status: str = Field("0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")


class PostCreate(PostBase):
    """创建岗位"""
    pass


class PostUpdate(PostBase):
    """更新岗位"""
    post_id: int = Field(..., description="岗位ID")


class PostInfo(PostBase):
    """岗位详细信息"""
    post_id: int = Field(..., description="岗位ID")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class PostQuery(BaseModel):
    """岗位查询参数"""
    post_code: Optional[str] = Field(None, description="岗位编码")
    post_name: Optional[str] = Field(None, description="岗位名称")
    status: Optional[str] = Field(None, description="状态（0正常 1停用）")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100) 