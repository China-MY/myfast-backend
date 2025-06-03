from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str
    role_key: str
    role_sort: int
    data_scope: str = "1"  # 数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）
    status: str = "0"
    remark: Optional[str] = None


class RoleCreate(RoleBase):
    """创建角色模型"""
    menu_ids: Optional[List[int]] = None
    dept_ids: Optional[List[int]] = None


class RoleUpdate(BaseModel):
    """更新角色模型"""
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    role_sort: Optional[int] = None
    data_scope: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None
    menu_ids: Optional[List[int]] = None
    dept_ids: Optional[List[int]] = None


class RoleInDB(RoleBase):
    """数据库角色模型"""
    role_id: int
    create_by: str = ""
    create_time: datetime
    update_by: str = ""
    update_time: Optional[datetime] = None
    del_flag: str = "0"

    class Config:
        orm_mode = True


class Role(RoleInDB):
    """角色信息模型"""
    pass


class RoleInfo(BaseModel):
    """角色简要信息模型"""
    role_id: int
    role_name: str
    role_key: str

    class Config:
        orm_mode = True


class RoleMenuTree(BaseModel):
    """角色权限树模型"""
    role_id: int
    role_name: str
    role_key: str
    data_scope: str
    menu_ids: List[int]
    dept_ids: Optional[List[int]] = None

    class Config:
        orm_mode = True 