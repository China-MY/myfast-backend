from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    """菜单基础模型"""
    menu_name: str
    parent_id: int = 0
    order_num: int = 0
    path: str = ""
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: int = 1
    is_cache: int = 0
    menu_type: str
    visible: str = "0"
    status: str = "0"
    perms: Optional[str] = None
    icon: str = "#"
    remark: str = ""


class MenuCreate(MenuBase):
    """创建菜单模型"""
    pass


class MenuUpdate(BaseModel):
    """更新菜单模型"""
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


class MenuInDB(MenuBase):
    """数据库菜单模型"""
    menu_id: int
    create_by: str = ""
    create_time: datetime
    update_by: str = ""
    update_time: Optional[datetime] = None

    class Config:
        orm_mode = True


class Menu(MenuInDB):
    """菜单信息模型"""
    pass


class MenuTree(BaseModel):
    """菜单树节点模型"""
    id: int
    label: str
    children: Optional[List["MenuTree"]] = None
    
    class Config:
        orm_mode = True


class RouterVo(BaseModel):
    """前端路由模型"""
    name: str
    path: str
    hidden: bool = False
    redirect: Optional[str] = None
    component: str
    always_show: Optional[bool] = None
    meta: dict
    children: Optional[List["RouterVo"]] = None

    class Config:
        orm_mode = True


# 更新 MenuTree 的 forward reference
MenuTree.update_forward_refs() 