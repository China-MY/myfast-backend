from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# 部门基础模型
class DeptBase(BaseModel):
    dept_id: int
    dept_name: str
    parent_id: int
    ancestors: str
    order_num: int
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True

# 创建部门的请求模型
class DeptCreate(BaseModel):
    dept_name: str
    parent_id: int = 0
    ancestors: Optional[str] = None
    order_num: int
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: str = "0"

# 更新部门的请求模型
class DeptUpdate(BaseModel):
    dept_name: Optional[str] = None
    parent_id: Optional[int] = None
    ancestors: Optional[str] = None
    order_num: Optional[int] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None

# 部门详细信息响应模型
class DeptInfo(DeptBase):
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 部门树节点模型
class DeptTreeNode(DeptBase):
    children: List["DeptTreeNode"] = []
    
    class Config:
        from_attributes = True

# 解决循环引用问题
DeptTreeNode.update_forward_refs()

# 部门查询请求模型
class DeptQuery(BaseModel):
    dept_name: Optional[str] = Field(None, description="部门名称")
    status: Optional[str] = Field(None, description="状态") 