from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.crud.base import CRUDBase
from app.models.dept import SysDept
from app.schemas.dept import DeptCreate, DeptUpdate, DeptTree


class CRUDDept(CRUDBase[SysDept, DeptCreate, DeptUpdate]):
    """部门数据访问层"""
    
    def get_all_with_filter(
        self, db: Session, *, dept_name: Optional[str] = None, status: Optional[str] = None
    ) -> List[SysDept]:
        """
        获取所有部门（带过滤条件）
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if dept_name:
            query = query.filter(self.model.dept_name.like(f"%{dept_name}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 部门排序
        depts = query.order_by(self.model.parent_id, self.model.order_num).all()
        
        return depts
    
    def get_tree(self, db: Session, *, status: Optional[str] = None) -> List[DeptTree]:
        """
        获取部门树
        """
        # 获取所有部门
        query = db.query(self.model)
        if status:
            query = query.filter(self.model.status == status)
        depts = query.order_by(self.model.parent_id, self.model.order_num).all()
        
        # 构建部门树
        return self._build_dept_tree(depts)
    
    def _build_dept_tree(self, depts: List[SysDept], parent_id: int = 0) -> List[DeptTree]:
        """
        递归构建部门树
        """
        tree = []
        for dept in depts:
            if dept.parent_id == parent_id:
                dept_dict = DeptTree.model_validate(dept)
                children = self._build_dept_tree(depts, dept.dept_id)
                dept_dict.children = children
                tree.append(dept_dict)
        return tree
    
    def has_children(self, db: Session, *, dept_id: int) -> bool:
        """
        判断部门是否有子部门
        """
        return db.query(self.model).filter(self.model.parent_id == dept_id).count() > 0
    
    def is_child(self, db: Session, *, parent_id: int, child_id: int) -> bool:
        """
        判断某个部门是否是另一个部门的子孙
        """
        # 获取所有部门
        depts = db.query(self.model).all()
        dept_map = {dept.dept_id: dept for dept in depts}
        
        # 查找子部门的所有祖先
        current_id = child_id
        visited = set()  # 防止循环引用
        
        while current_id != 0 and current_id not in visited:
            visited.add(current_id)
            current_dept = dept_map.get(current_id)
            if not current_dept:
                break
                
            current_id = current_dept.parent_id
            if current_id == parent_id:
                return True
                
        return False
    
    def create(self, db: Session, *, obj_in: DeptCreate, creator_id: int) -> SysDept:
        """
        创建部门
        """
        # 获取父部门信息
        parent_dept = None
        ancestors = "0"
        if obj_in.parent_id != 0:
            parent_dept = db.query(self.model).filter(self.model.dept_id == obj_in.parent_id).first()
            if parent_dept:
                ancestors = parent_dept.ancestors + "," + str(obj_in.parent_id)
        
        db_obj = self.model(
            dept_name=obj_in.dept_name,
            parent_id=obj_in.parent_id,
            ancestors=ancestors,
            order_num=obj_in.order_num,
            leader=obj_in.leader,
            phone=obj_in.phone,
            email=obj_in.email,
            status=obj_in.status,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysDept, obj_in: Union[DeptUpdate, Dict[str, Any]], updater_id: int
    ) -> SysDept:
        """
        更新部门
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        # 如果更新了parent_id，需要更新ancestors
        if "parent_id" in update_data and update_data["parent_id"] != db_obj.parent_id:
            parent_id = update_data["parent_id"]
            ancestors = "0"
            
            if parent_id != 0:
                parent_dept = db.query(self.model).filter(self.model.dept_id == parent_id).first()
                if parent_dept:
                    ancestors = parent_dept.ancestors + "," + str(parent_id)
            
            update_data["ancestors"] = ancestors
            
            # 更新所有子部门的ancestors
            self._update_children_ancestors(db, db_obj.dept_id, ancestors + "," + str(db_obj.dept_id))
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def _update_children_ancestors(self, db: Session, dept_id: int, new_ancestors: str) -> None:
        """
        更新子部门的祖先列表
        """
        children = db.query(self.model).filter(self.model.parent_id == dept_id).all()
        for child in children:
            child.ancestors = new_ancestors
            db.add(child)
            
            # 递归更新子孙部门
            next_ancestors = new_ancestors + "," + str(child.dept_id)
            self._update_children_ancestors(db, child.dept_id, next_ancestors)
        
        if children:
            db.commit()


# 实例化
dept = CRUDDept(SysDept) 