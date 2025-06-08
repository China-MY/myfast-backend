from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DeptBase(BaseModel):
    """部门基本属性"""
    dept_name: Optional[str] = None
    parent_id: Optional[int] = 0
    ancestors: Optional[str] = None
    order_num: Optional[int] = 0
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = "0"


class DeptCreate(DeptBase):
    """创建部门模型"""
    dept_name: str


class DeptUpdate(DeptBase):
    """更新部门模型"""
    pass


class DeptInDB(DeptBase):
    """数据库部门模型"""
    dept_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DeptOut(DeptInDB):
    """部门输出模型"""
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DeptTree(DeptBase):
    """部门树模型"""
    dept_id: int
    children: List['DeptTree'] = []
    
    model_config = ConfigDict(from_attributes=True)


# 递归引用需要更新
DeptTree.model_rebuild() 