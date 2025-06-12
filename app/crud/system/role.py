from typing import Dict, List, Optional, Union, Tuple, Any
from sqlalchemy.orm import Session

from app.crud.utils.base import CRUDBase
from app.models.system.role import SysRole
from app.models.utils.relation import SysRoleMenu, SysUserRole
from app.schemas.system.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[SysRole, RoleCreate, RoleUpdate]):
    """角色数据访问层"""
    
    def get_by_id(self, db: Session, *, role_id: int) -> Optional[SysRole]:
        """
        通过角色ID获取角色
        """
        return db.query(self.model).filter(self.model.role_id == role_id).first()
    
    def get_by_name(self, db: Session, *, role_name: str) -> Optional[SysRole]:
        """
        通过角色名称获取角色
        """
        return db.query(self.model).filter(self.model.role_name == role_name).first()
    
    def get_by_key(self, db: Session, *, role_key: str) -> Optional[SysRole]:
        """
        通过角色标识获取角色
        """
        return db.query(self.model).filter(self.model.role_key == role_key).first()
    
    def get_multi_with_filter(
        self, db: Session, *, skip: int = 0, limit: int = 100, 
        role_name: Optional[str] = None, role_key: Optional[str] = None, status: Optional[str] = None
    ) -> Tuple[List[SysRole], int]:
        """
        获取角色列表（带过滤条件）
        """
        query = db.query(self.model)
        
        # 打印调试信息
        print(f"查询角色列表参数: skip={skip}, limit={limit}, role_name={role_name}, role_key={role_key}, status={status}")
        
        # 应用过滤条件
        if role_name:
            query = query.filter(self.model.role_name.like(f"%{role_name}%"))
        if role_key:
            query = query.filter(self.model.role_key.like(f"%{role_key}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 计算总数
        total = query.count()
        print(f"查询到的角色总数: {total}")
        
        # 应用分页并返回数据
        roles = query.order_by(self.model.role_sort).offset(skip).limit(limit).all()
        
        # 打印查询结果
        role_info = [f"ID:{role.role_id}, 名称:{role.role_name}" for role in roles]
        print(f"查询到的角色列表: {role_info}")
        
        return roles, total
    
    def get_enabled_roles(self, db: Session) -> List[SysRole]:
        """
        获取启用状态的角色列表
        """
        return db.query(self.model).filter(self.model.status == "0").order_by(self.model.role_sort).all()
    
    def create(self, db: Session, *, obj_in: RoleCreate, creator_id: int) -> SysRole:
        """
        创建角色
        """
        db_obj = self.model(
            role_name=obj_in.role_name,
            role_key=obj_in.role_key,
            role_sort=obj_in.role_sort,
            data_scope=obj_in.data_scope,
            status=obj_in.status,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysRole, obj_in: Union[RoleUpdate, Dict[str, Any]], updater_id: int
    ) -> SysRole:
        """
        更新角色
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def remove(self, db: Session, *, role_id: int) -> SysRole:
        """
        删除角色
        """
        # 先删除角色菜单关联数据
        db.execute(SysRoleMenu.delete().where(SysRoleMenu.c.role_id == role_id))
        
        return super().remove(db, id=role_id)
    
    def has_users(self, db: Session, *, role_id: int) -> bool:
        """
        检查角色是否有关联用户
        """
        # 使用Table对象正确的查询方式
        result = db.execute(SysUserRole.select().where(SysUserRole.c.role_id == role_id))
        return result.rowcount > 0
    
    def get_role_menu_ids(self, db: Session, *, role_id: int) -> List[int]:
        """
        获取角色关联的菜单ID列表
        """
        print(f"[DEBUG] 获取角色菜单IDs: role_id={role_id}")
        # 使用Table对象查询
        result = db.execute(SysRoleMenu.select().where(SysRoleMenu.c.role_id == role_id))
        menu_ids = [row.menu_id for row in result]
        print(f"[DEBUG] 找到的菜单IDs: {menu_ids}")
        return menu_ids
    
    def set_role_menus(self, db: Session, *, role_id: int, menu_ids: List[int]) -> None:
        """
        设置角色菜单权限
        """
        # 删除原有的角色菜单关联数据
        db.execute(SysRoleMenu.delete().where(SysRoleMenu.c.role_id == role_id))
        
        # 添加新的角色菜单关联数据
        for menu_id in menu_ids:
            db.execute(SysRoleMenu.insert().values(role_id=role_id, menu_id=menu_id))
        
        db.commit()


# 实例化
role = CRUDRole(SysRole) 