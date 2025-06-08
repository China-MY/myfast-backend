from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    """岗位基本属性"""
    post_name: Optional[str] = None
    post_code: Optional[str] = None
    post_sort: Optional[int] = 0
    status: Optional[str] = "0"
    remark: Optional[str] = None


class PostCreate(PostBase):
    """创建岗位模型"""
    post_name: str
    post_code: str
    post_sort: int


class PostUpdate(PostBase):
    """更新岗位模型"""
    pass


class PostInDB(PostBase):
    """数据库岗位模型"""
    post_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class PostOut(PostInDB):
    """岗位输出模型"""
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) 