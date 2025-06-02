from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# 部门基础模型
class DeptBase(BaseModel):
    """部门基础信息"""
    parent_id: int = Field(0, description="父部门ID")
    dept_name: str = Field(..., description="部门名称")
    order_num: int = Field(0, description="显示顺序")
    leader: Optional[str] = Field(None, description="负责人")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    status: str = Field("0", description="部门状态（0正常 1停用）")

# 创建部门请求模型
class DeptCreate(DeptBase):
    """创建部门"""
    pass

# 更新部门请求模型
class DeptUpdate(DeptBase):
    """更新部门"""
    dept_id: int = Field(..., description="部门ID")

# 部门树节点
class DeptTreeNode(BaseModel):
    id: int = Field(..., description="部门ID")
    label: str = Field(..., description="部门名称")
    children: Optional[List['DeptTreeNode']] = Field(None, description="子部门")

# 部门信息响应模型
class DeptInfo(DeptBase):
    """部门详细信息"""
    dept_id: int = Field(..., description="部门ID")
    ancestors: str = Field("", description="祖级列表")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

class DeptQuery(BaseModel):
    """部门查询参数"""
    dept_name: Optional[str] = Field(None, description="部门名称")
    status: Optional[str] = Field(None, description="部门状态（0正常 1停用）") 