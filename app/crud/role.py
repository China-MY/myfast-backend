from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.crud.base import CRUDBase
from app.models.role import Role, role_menu, role_dept
from app.models.menu import Menu
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_role_key(self, db: Session, *, role_key: str) -> Optional[Role]:
        """
        根据角色标识获取角色信息
        """
        return db.query(self.model).filter(
            self.model.role_key == role_key,
            self.model.del_flag == "0"
        ).first()
    
    def get_by_role_name(self, db: Session, *, role_name: str) -> Optional[Role]:
        """
        根据角色名称获取角色信息
        """
        return db.query(self.model).filter(
            self.model.role_name == role_name,
            self.model.del_flag == "0"
        ).first()
    
    def get_all_roles(self, db: Session, *, status: Optional[str] = None) -> List[Role]:
        """
        获取所有角色
        """
        query = db.query(self.model).filter(self.model.del_flag == "0")
        if status:
            query = query.filter(self.model.status == status)
        return query.order_by(self.model.role_sort).all()
    
    def get_role_list(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        role_name: Optional[str] = None,
        role_key: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取角色列表
        """
        query = db.query(self.model).filter(self.model.del_flag == "0")
        
        # 构建查询条件
        if role_name:
            query = query.filter(self.model.role_name.like(f"%{role_name}%"))
        if role_key:
            query = query.filter(self.model.role_key.like(f"%{role_key}%"))
        if status:
            query = query.filter(self.model.status == status)
            
        # 统计总数
        total = query.count()
        
        # 分页查询
        roles = query.order_by(self.model.role_sort).offset(skip).limit(limit).all()
        
        return {"items": roles, "total": total}
    
    def create_with_menus(
        self, 
        db: Session, 
        *, 
        obj_in: RoleCreate
    ) -> Role:
        """
        创建角色（同时设置菜单权限）
        """
        # 创建角色基础信息
        db_obj = Role(
            role_name=obj_in.role_name,
            role_key=obj_in.role_key,
            role_sort=obj_in.role_sort,
            data_scope=obj_in.data_scope,
            status=obj_in.status,
            remark=obj_in.remark
        )
        db.add(db_obj)
        db.flush()
        
        # 设置角色菜单关系
        if obj_in.menu_ids:
            self.update_role_menus(db, db_obj, obj_in.menu_ids)
            
        # 设置角色部门关系（数据权限）
        if obj_in.dept_ids and obj_in.data_scope == "2":  # 自定义数据权限
            self.update_role_depts(db, db_obj, obj_in.dept_ids)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_menus(
        self,
        db: Session,
        *,
        db_obj: Role,
        obj_in: RoleUpdate
    ) -> Role:
        """
        更新角色（同时更新菜单权限）
        """
        # 更新角色基础信息
        update_data = obj_in.dict(exclude={"menu_ids", "dept_ids"})
        for field in update_data:
            if update_data[field] is not None:
                setattr(db_obj, field, update_data[field])
        
        # 更新角色菜单关系
        if obj_in.menu_ids is not None:
            self.update_role_menus(db, db_obj, obj_in.menu_ids)
            
        # 更新角色部门关系（数据权限）
        if obj_in.dept_ids is not None and db_obj.data_scope == "2":  # 自定义数据权限
            self.update_role_depts(db, db_obj, obj_in.dept_ids)
        elif db_obj.data_scope != "2":
            # 如果不是自定义数据权限，则删除角色与部门的关联
            db.execute(role_dept.delete().where(role_dept.c.role_id == db_obj.role_id))
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def update_role_status(
        self,
        db: Session,
        *,
        role_id: int,
        status: str
    ) -> Role:
        """
        更新角色状态
        """
        db_obj = db.query(self.model).filter(self.model.role_id == role_id).first()
        if db_obj:
            db_obj.status = status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def update_role_menus(
        self,
        db: Session,
        role: Role,
        menu_ids: List[int]
    ) -> None:
        """
        更新角色菜单关系
        """
        # 删除原有菜单关联
        db.execute(role_menu.delete().where(role_menu.c.role_id == role.role_id))
        
        # 添加新的菜单关联
        for menu_id in menu_ids:
            db.execute(
                role_menu.insert().values(role_id=role.role_id, menu_id=menu_id)
            )
    
    def update_role_depts(
        self,
        db: Session,
        role: Role,
        dept_ids: List[int]
    ) -> None:
        """
        更新角色部门关系（数据权限）
        """
        # 删除原有部门关联
        db.execute(role_dept.delete().where(role_dept.c.role_id == role.role_id))
        
        # 添加新的部门关联
        for dept_id in dept_ids:
            db.execute(
                role_dept.insert().values(role_id=role.role_id, dept_id=dept_id)
            )
    
    def get_role_menus(self, db: Session, role_id: int) -> List[Menu]:
        """
        获取角色菜单列表
        """
        return db.query(Menu).join(
            role_menu, role_menu.c.menu_id == Menu.menu_id
        ).filter(
            role_menu.c.role_id == role_id
        ).order_by(Menu.parent_id, Menu.order_num).all()
    
    def get_role_menu_ids(self, db: Session, role_id: int) -> List[int]:
        """
        获取角色菜单ID列表
        """
        menus = db.query(role_menu.c.menu_id).filter(
            role_menu.c.role_id == role_id
        ).all()
        return [menu[0] for menu in menus]
    
    def get_role_dept_ids(self, db: Session, role_id: int) -> List[int]:
        """
        获取角色部门ID列表（数据权限）
        """
        depts = db.query(role_dept.c.dept_id).filter(
            role_dept.c.role_id == role_id
        ).all()
        return [dept[0] for dept in depts]


role = CRUDRole(Role) 