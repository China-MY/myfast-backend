from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 角色基础模型
class RoleBase(BaseModel):
    role_name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色权限字符串")
    role_sort: int = Field(..., description="显示顺序")
    data_scope: Optional[str] = Field("1", description="数据范围（1全部数据权限 2自定数据权限 3本部门数据权限 4本部门及以下数据权限）")
    status: str = Field("0", description="角色状态（0正常 1停用）")
    remark: Optional[str] = Field(None, description="备注")

# 创建角色请求模型
class RoleCreate(RoleBase):
    menu_ids: List[int] = Field([], description="菜单ID列表")
    dept_ids: Optional[List[int]] = Field([], description="部门ID列表")

# 更新角色请求模型
class RoleUpdate(RoleBase):
    role_id: int = Field(..., description="角色ID")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")
    dept_ids: Optional[List[int]] = Field(None, description="部门ID列表")

# 角色查询参数模型
class RoleQuery(BaseModel):
    role_name: Optional[str] = Field(None, description="角色名称")
    role_key: Optional[str] = Field(None, description="角色权限字符串")
    status: Optional[str] = Field(None, description="角色状态")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")

# 角色信息响应模型
class RoleInfo(RoleBase):
    role_id: int = Field(..., description="角色ID")
    create_time: datetime = Field(..., description="创建时间")
    menu_ids: List[int] = Field([], description="菜单ID列表")
    dept_ids: List[int] = Field([], description="部门ID列表")
    
    class Config:
        from_attributes = True 