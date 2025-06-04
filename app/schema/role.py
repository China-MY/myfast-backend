from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 角色基础模型
class RoleBase(BaseModel):
    role_id: int
    role_name: str
    role_key: str
    role_sort: int
    status: str
    
    class Config:
        from_attributes = True

# 创建角色的请求模型
class RoleCreate(BaseModel):
    role_name: str
    role_key: str
    role_sort: int
    status: str = "0"
    remark: Optional[str] = None
    menu_ids: List[int] = []
    dept_ids: Optional[List[int]] = None
    data_scope: str = "1"

# 更新角色的请求模型
class RoleUpdate(BaseModel):
    role_id: int
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    role_sort: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None
    menu_ids: Optional[List[int]] = None
    dept_ids: Optional[List[int]] = None
    data_scope: Optional[str] = None

# 角色详细信息响应模型
class RoleInfo(RoleBase):
    remark: Optional[str] = None
    create_time: Optional[datetime] = None
    menu_ids: List[int] = []
    dept_ids: List[int] = []
    data_scope: str
    
    class Config:
        from_attributes = True

# 角色分页查询请求模型
class RoleQuery(BaseModel):
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页显示条数")
    role_name: Optional[str] = Field(None, description="角色名称")
    role_key: Optional[str] = Field(None, description="角色权限字符")
    status: Optional[str] = Field(None, description="状态")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间") 