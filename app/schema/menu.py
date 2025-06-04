from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 菜单基础模型
class MenuBase(BaseModel):
    menu_id: int
    menu_name: str
    parent_id: int
    order_num: int
    path: str
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: int
    is_cache: int
    menu_type: str
    visible: str
    status: str
    perms: Optional[str] = None
    icon: str
    
    class Config:
        from_attributes = True

# 创建菜单的请求模型
class MenuCreate(BaseModel):
    menu_name: str
    parent_id: int = 0
    order_num: int
    path: str
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: int = 1
    is_cache: int = 0
    menu_type: str
    visible: str = "0"
    status: str = "0"
    perms: Optional[str] = None
    icon: str = "#"
    remark: Optional[str] = None

# 更新菜单的请求模型
class MenuUpdate(BaseModel):
    menu_name: Optional[str] = None
    parent_id: Optional[int] = None
    order_num: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: Optional[int] = None
    is_cache: Optional[int] = None
    menu_type: Optional[str] = None
    visible: Optional[str] = None
    status: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    remark: Optional[str] = None

# 菜单详细信息响应模型
class MenuInfo(MenuBase):
    remark: Optional[str] = None
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 菜单树节点模型
class MenuTreeNode(MenuBase):
    children: List["MenuTreeNode"] = []
    
    class Config:
        from_attributes = True

# 解决循环引用问题
MenuTreeNode.update_forward_refs()

# 菜单查询请求模型
class MenuQuery(BaseModel):
    menu_name: Optional[str] = Field(None, description="菜单名称")
    status: Optional[str] = Field(None, description="状态") 