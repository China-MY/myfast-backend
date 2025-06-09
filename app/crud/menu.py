from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import traceback

from app.crud.base import CRUDBase
from app.models.menu import SysMenu
from app.models.role import SysRole
from app.models.relation import SysRoleMenu, SysUserRole
from app.models.user import SysUser
from app.schemas.menu import MenuCreate, MenuUpdate, MenuTree


class CRUDMenu(CRUDBase[SysMenu, MenuCreate, MenuUpdate]):
    """菜单数据访问层"""
    
    def get_all_with_filter(
        self, db: Session, *, menu_name: Optional[str] = None, status: Optional[str] = None
    ) -> List[SysMenu]:
        """
        获取所有菜单（带过滤条件）
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if menu_name:
            query = query.filter(self.model.menu_name.like(f"%{menu_name}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 菜单排序
        menus = query.order_by(self.model.parent_id, self.model.order_num).all()
        
        return menus
    
    def get_tree(self, db: Session, status: Optional[str] = None) -> List[MenuTree]:
        """
        获取菜单树
        """
        # 获取所有菜单
        query = db.query(self.model)
        if status:
            query = query.filter(self.model.status == status)
        menus = query.order_by(self.model.parent_id, self.model.order_num).all()
        
        # 构建菜单树
        return self._build_menu_tree(menus)
    
    def _build_menu_tree(self, menus: List[SysMenu], parent_id: int = 0) -> List[MenuTree]:
        """
        递归构建菜单树
        """
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                try:
                    # 在验证前转换字段类型
                    menu_dict = {
                        "menu_id": menu.menu_id,
                        "menu_name": menu.menu_name,
                        "parent_id": menu.parent_id,
                        "order_num": menu.order_num,
                        "path": menu.path,
                        "component": menu.component,
                        "query": menu.query,  # 修正字段名
                        "is_frame": str(menu.is_frame) if menu.is_frame is not None else "1",  # 确保是字符串
                        "is_cache": str(menu.is_cache) if menu.is_cache is not None else "0",  # 确保是字符串
                        "menu_type": menu.menu_type,
                        "visible": menu.visible,
                        "status": menu.status,
                        "perms": menu.perms,
                        "icon": menu.icon,
                        "remark": menu.remark
                    }
                    
                    # 打印调试信息
                    print(f"[DEBUG] 处理菜单 ID: {menu.menu_id}, 名称: {menu.menu_name}")
                    print(f"[DEBUG] is_frame 类型: {type(menu.is_frame)}, 值: {menu.is_frame}")
                    print(f"[DEBUG] is_cache 类型: {type(menu.is_cache)}, 值: {menu.is_cache}")
                    
                    # 使用model_validate处理字典
                    menu_tree = MenuTree.model_validate(menu_dict)
                    
                    # 递归获取子菜单
                    children = self._build_menu_tree(menus, menu.menu_id)
                    menu_tree.children = children
                    tree.append(menu_tree)
                except Exception as e:
                    print(f"[ERROR] 构建菜单树错误, 菜单ID: {menu.menu_id}, 错误: {str(e)}")
                    print(f"[ERROR] 详细错误: {traceback.format_exc()}")
                    # 记录问题，但不阻止其他菜单的处理
                    continue
        return tree
    
    def get_user_menus(self, db: Session, user: SysUser) -> List[MenuTree]:
        """
        获取用户可访问的菜单列表
        """
        # 超级管理员可以访问所有菜单
        user_id = user.user_id
        if self._is_admin(user):
            menus = db.query(self.model).filter(
                self.model.status == "0",
                self.model.menu_type.in_(["M", "C"])
            ).order_by(self.model.parent_id, self.model.order_num).all()
            return self._build_menu_tree(menus)
        
        # 获取用户角色ID列表
        user_role_ids = db.query(SysUserRole.role_id).filter(SysUserRole.user_id == user_id).all()
        user_role_ids = [r[0] for r in user_role_ids]
        
        # 获取角色菜单ID列表
        role_menu_ids = db.query(SysRoleMenu.c.menu_id).filter(
            SysRoleMenu.c.role_id.in_(user_role_ids)
        ).distinct().all()
        role_menu_ids = [r[0] for r in role_menu_ids]
        
        # 获取菜单列表
        menus = db.query(self.model).filter(
            self.model.menu_id.in_(role_menu_ids),
            self.model.status == "0",
            self.model.menu_type.in_(["M", "C"])
        ).order_by(self.model.parent_id, self.model.order_num).all()
        
        return self._build_menu_tree(menus)
    
    def _is_admin(self, user: SysUser) -> bool:
        """
        判断用户是否是超级管理员
        """
        # 检查用户是否拥有admin角色
        admin_roles = [role for role in user.roles if role.role_key == "admin"]
        return len(admin_roles) > 0
    
    def has_children(self, db: Session, *, menu_id: int) -> bool:
        """
        判断菜单是否有子菜单
        """
        return db.query(self.model).filter(self.model.parent_id == menu_id).count() > 0
    
    def is_child(self, db: Session, *, parent_id: int, child_id: int) -> bool:
        """
        判断某个菜单是否是另一个菜单的子孙
        """
        # 获取所有菜单
        menus = db.query(self.model).all()
        menu_map = {menu.menu_id: menu for menu in menus}
        
        # 查找子菜单的所有祖先
        current_id = child_id
        visited = set()  # 防止循环引用
        
        while current_id != 0 and current_id not in visited:
            visited.add(current_id)
            current_menu = menu_map.get(current_id)
            if not current_menu:
                break
                
            current_id = current_menu.parent_id
            if current_id == parent_id:
                return True
                
        return False
    
    def create(self, db: Session, *, obj_in: MenuCreate, creator_id: int) -> SysMenu:
        """
        创建菜单
        """
        db_obj = self.model(
            menu_name=obj_in.menu_name,
            parent_id=obj_in.parent_id,
            order_num=obj_in.order_num,
            path=obj_in.path,
            component=obj_in.component,
            query=obj_in.query,  # 修正字段名
            is_frame=obj_in.is_frame,
            is_cache=obj_in.is_cache,
            menu_type=obj_in.menu_type,
            visible=obj_in.visible,
            status=obj_in.status,
            perms=obj_in.perms,
            icon=obj_in.icon,
            remark=obj_in.remark,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysMenu, obj_in: Union[MenuUpdate, Dict[str, Any]], updater_id: int
    ) -> SysMenu:
        """
        更新菜单
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def get_role_menu_ids(self, db: Session, *, role_id: int) -> List[int]:
        """
        获取角色关联的菜单ID列表
        """
        print(f"[DEBUG] 正在菜单模块中查询角色菜单IDs: role_id={role_id}")
        result = db.execute(SysRoleMenu.select().where(SysRoleMenu.c.role_id == role_id))
        menu_ids = [row.menu_id for row in result]
        print(f"[DEBUG] 菜单模块找到的菜单IDs: {menu_ids}")
        return menu_ids


# 实例化
menu = CRUDMenu(SysMenu) 