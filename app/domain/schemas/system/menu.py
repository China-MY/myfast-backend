from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 菜单基础模型
class MenuBase(BaseModel):
    menu_name: str = Field(..., description="菜单名称")
    parent_id: int = Field(0, description="父菜单ID")
    order_num: int = Field(0, description="显示顺序")
    path: Optional[str] = Field("", description="路由地址")
    component: Optional[str] = Field(None, description="组件路径")
    query: Optional[str] = Field(None, description="路由参数")
    is_frame: int = Field(1, description="是否为外链（0是 1否）")
    is_cache: int = Field(0, description="是否缓存（0缓存 1不缓存）")
    menu_type: str = Field(..., description="菜单类型（M目录 C菜单 F按钮）")
    visible: str = Field("0", description="菜单状态（0显示 1隐藏）")
    status: str = Field("0", description="菜单状态（0正常 1停用）")
    perms: Optional[str] = Field(None, description="权限标识")
    icon: Optional[str] = Field("#", description="菜单图标")
    remark: Optional[str] = Field("", description="备注")

# 创建菜单请求模型
class MenuCreate(MenuBase):
    pass

# 更新菜单请求模型
class MenuUpdate(MenuBase):
    menu_id: int = Field(..., description="菜单ID")

# 菜单树节点
class MenuTreeNode(BaseModel):
    id: int = Field(..., description="菜单ID")
    label: str = Field(..., description="菜单名称")
    children: Optional[List['MenuTreeNode']] = Field(None, description="子菜单")

# 菜单信息响应模型
class MenuInfo(MenuBase):
    menu_id: int = Field(..., description="菜单ID")
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True 