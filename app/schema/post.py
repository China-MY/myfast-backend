from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 岗位基础模型
class PostBase(BaseModel):
    post_id: int
    post_code: str
    post_name: str
    post_sort: int
    status: str
    
    class Config:
        from_attributes = True

# 创建岗位的请求模型
class PostCreate(BaseModel):
    post_code: str
    post_name: str
    post_sort: int
    status: str = "0"
    remark: Optional[str] = None

# 更新岗位的请求模型
class PostUpdate(BaseModel):
    post_code: Optional[str] = None
    post_name: Optional[str] = None
    post_sort: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None

# 岗位详细信息响应模型
class PostInfo(PostBase):
    remark: Optional[str] = None
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 岗位查询请求模型
class PostQuery(BaseModel):
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页显示条数")
    post_code: Optional[str] = Field(None, description="岗位编码")
    post_name: Optional[str] = Field(None, description="岗位名称")
    status: Optional[str] = Field(None, description="状态") 