from typing import List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MenuBase(BaseModel):
    """菜单基本属性"""
    menu_name: Optional[str] = None
    parent_id: Optional[int] = 0
    order_num: Optional[int] = 0
    path: Optional[str] = None
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: Optional[Union[str, int]] = "1"
    is_cache: Optional[Union[str, int]] = "0"
    menu_type: Optional[str] = "M"
    visible: Optional[str] = "0"
    status: Optional[str] = "0"
    perms: Optional[str] = None
    icon: Optional[str] = "#"
    remark: Optional[str] = None


class MenuCreate(MenuBase):
    """创建菜单模型"""
    menu_name: str
    menu_type: str


class MenuUpdate(MenuBase):
    """更新菜单模型"""
    pass


class MenuInDB(MenuBase):
    """数据库菜单模型"""
    menu_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MenuOut(MenuInDB):
    """菜单输出模型"""
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MenuTree(MenuBase):
    """菜单树模型"""
    menu_id: int
    children: List['MenuTree'] = []
    
    model_config = ConfigDict(from_attributes=True)


# 递归引用需要更新
MenuTree.model_rebuild() 