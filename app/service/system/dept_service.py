from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.entity.sys_dept import SysDept
from app.common.constants import StatusEnum, DeleteFlagEnum
from app.common.exception import BusinessException

class DeptService:
    """部门服务类"""
    
    @staticmethod
    def get_dept_by_id(db: Session, dept_id: int) -> Optional[SysDept]:
        """根据部门ID获取部门信息"""
        return db.query(SysDept).filter(
            SysDept.dept_id == dept_id,
            SysDept.del_flag == DeleteFlagEnum.NORMAL
        ).first()
    
    @staticmethod
    def get_depts(
        db: Session,
        dept_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[SysDept]:
        """获取部门列表"""
        query = db.query(SysDept).filter(SysDept.del_flag == DeleteFlagEnum.NORMAL)
        
        # 应用过滤条件
        if dept_name:
            query = query.filter(SysDept.dept_name.like(f"%{dept_name}%"))
        if status:
            query = query.filter(SysDept.status == status)
        
        # 按照父部门ID和排序字段排序
        query = query.order_by(SysDept.parent_id, SysDept.order_num)
        
        return query.all()
    
    @staticmethod
    def create_dept(
        db: Session, 
        dept_data: Dict[str, Any],
        current_user_name: str
    ) -> SysDept:
        """创建部门"""
        # 验证父部门
        if dept_data.get("parent_id") and dept_data.get("parent_id") != 0:
            parent_dept = DeptService.get_dept_by_id(db, dept_data["parent_id"])
            if not parent_dept:
                raise BusinessException(code=400, msg="父部门不存在")
            
            # 如果父部门被禁用，则不允许创建子部门
            if parent_dept.status == StatusEnum.DISABLE:
                raise BusinessException(code=400, msg="父部门已被停用，不允许创建子部门")
            
            # 设置祖级列表
            if not dept_data.get("ancestors"):
                if parent_dept.parent_id == 0:
                    dept_data["ancestors"] = str(parent_dept.dept_id)
                else:
                    dept_data["ancestors"] = f"{parent_dept.ancestors},{parent_dept.dept_id}"
        else:
            dept_data["ancestors"] = "0"
        
        # 设置创建信息
        dept_data["create_by"] = current_user_name
        dept_data["create_time"] = datetime.now()
        
        # 创建部门
        dept = SysDept(**dept_data)
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept
    
    @staticmethod
    def update_dept(
        db: Session, 
        dept: SysDept,
        dept_data: Dict[str, Any],
        current_user_name: str
    ) -> SysDept:
        """更新部门"""
        # 不能将部门的父ID设置为自己或其子部门的ID
        if "parent_id" in dept_data and dept_data["parent_id"] != 0:
            if dept_data["parent_id"] == dept.dept_id:
                raise BusinessException(code=400, msg="父部门不能选择自己")
            
            # 检查是否选择了子部门作为父部门
            children = DeptService.get_child_depts(db, dept.dept_id)
            child_ids = [child.dept_id for child in children]
            if dept_data["parent_id"] in child_ids:
                raise BusinessException(code=400, msg="父部门不能选择子部门")
            
            # 验证父部门是否存在
            parent_dept = DeptService.get_dept_by_id(db, dept_data["parent_id"])
            if not parent_dept:
                raise BusinessException(code=400, msg="父部门不存在")
            
            # 如果父部门被禁用，则不允许设置
            if parent_dept.status == StatusEnum.DISABLE:
                raise BusinessException(code=400, msg="父部门已被停用，不允许设置")
            
            # 更新祖级列表
            if parent_dept.parent_id == 0:
                dept_data["ancestors"] = str(parent_dept.dept_id)
            else:
                dept_data["ancestors"] = f"{parent_dept.ancestors},{parent_dept.dept_id}"
        
        # 设置更新信息
        dept_data["update_by"] = current_user_name
        dept_data["update_time"] = datetime.now()
        
        # 更新部门信息
        for key, value in dept_data.items():
            if hasattr(dept, key) and value is not None:
                setattr(dept, key, value)
        
        db.add(dept)
        db.commit()
        db.refresh(dept)
        
        # 如果更新了父部门，需要更新所有子部门的祖级列表
        if "parent_id" in dept_data:
            DeptService.update_children_ancestors(db, dept)
        
        return dept
    
    @staticmethod
    def delete_dept(db: Session, dept_id: int, current_user_name: str) -> bool:
        """删除部门（逻辑删除）"""
        dept = DeptService.get_dept_by_id(db, dept_id)
        if not dept:
            return False
        
        # 检查是否有子部门
        children = DeptService.get_child_depts(db, dept_id)
        if children:
            raise BusinessException(code=400, msg="存在子部门，不允许删除")
        
        # 检查部门是否已分配角色
        if dept.roles and len(dept.roles) > 0:
            raise BusinessException(code=400, msg="部门已分配角色，不允许删除")
        
        # 检查部门是否已分配用户
        if dept.users and len(dept.users) > 0:
            raise BusinessException(code=400, msg="部门已分配用户，不允许删除")
        
        # 逻辑删除
        dept.del_flag = DeleteFlagEnum.DELETED
        dept.update_by = current_user_name
        dept.update_time = datetime.now()
        
        db.add(dept)
        db.commit()
        return True
    
    @staticmethod
    def get_child_depts(db: Session, parent_id: int) -> List[SysDept]:
        """获取子部门列表"""
        return db.query(SysDept).filter(
            SysDept.parent_id == parent_id,
            SysDept.del_flag == DeleteFlagEnum.NORMAL
        ).all()
    
    @staticmethod
    def update_children_ancestors(db: Session, dept: SysDept) -> None:
        """更新子部门的祖级列表"""
        children = DeptService.get_child_depts(db, dept.dept_id)
        for child in children:
            child.ancestors = f"{dept.ancestors},{dept.dept_id}"
            db.add(child)
            # 递归更新子部门的子部门
            DeptService.update_children_ancestors(db, child)
        
        db.commit()
    
    @staticmethod
    def build_dept_tree(depts: List[SysDept], parent_id: int = 0) -> List[Dict[str, Any]]:
        """构建部门树"""
        tree = []
        for dept in depts:
            if dept.parent_id == parent_id:
                dept_dict = {
                    "dept_id": dept.dept_id,
                    "dept_name": dept.dept_name,
                    "parent_id": dept.parent_id,
                    "ancestors": dept.ancestors,
                    "order_num": dept.order_num,
                    "leader": dept.leader,
                    "phone": dept.phone,
                    "email": dept.email,
                    "status": dept.status,
                    "create_time": dept.create_time,
                    "children": DeptService.build_dept_tree(depts, dept.dept_id)
                }
                tree.append(dept_dict)
        return tree
    
    @staticmethod
    def get_dept_tree(db: Session) -> List[Dict[str, Any]]:
        """获取部门树"""
        depts = db.query(SysDept).filter(
            SysDept.status == StatusEnum.NORMAL,
            SysDept.del_flag == DeleteFlagEnum.NORMAL
        ).order_by(SysDept.parent_id, SysDept.order_num).all()
        
        return DeptService.build_dept_tree(depts) 