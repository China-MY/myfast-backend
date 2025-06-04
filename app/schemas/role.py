from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    """角色基本属性"""
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    role_sort: Optional[int] = None
    data_scope: Optional[str] = "1"
    status: Optional[str] = "0"


class RoleCreate(RoleBase):
    """创建角色模型"""
    role_name: str
    role_key: str
    role_sort: int
    menu_ids: Optional[List[int]] = []


class RoleUpdate(RoleBase):
    """更新角色模型"""
    menu_ids: Optional[List[int]] = None


class RoleInDB(RoleBase):
    """数据库角色模型"""
    role_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Role(RoleInDB):
    """返回角色模型"""
    menus: Optional[List[dict]] = []
    
    model_config = ConfigDict(from_attributes=True) 