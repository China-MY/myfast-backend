from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.crud.base import CRUDBase
from app.models.menu import Menu
from app.models.role import role_menu
from app.schemas.menu import MenuCreate, MenuUpdate


class CRUDMenu(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def get_by_name(self, db: Session, *, menu_name: str, parent_id: int = 0) -> Optional[Menu]:
        """
        通过菜单名称和父菜单ID获取菜单信息
        """
        return db.query(self.model).filter(
            self.model.menu_name == menu_name,
            self.model.parent_id == parent_id
        ).first()
    
    def get_by_id(self, db: Session, menu_id: int) -> Optional[Menu]:
        """
        通过菜单ID获取菜单信息
        """
        return db.query(self.model).filter(
            self.model.menu_id == menu_id
        ).first()
    
    def get_children_by_parent_id(self, db: Session, parent_id: int) -> List[Menu]:
        """
        获取指定父菜单ID的所有子菜单
        """
        return db.query(self.model).filter(
            self.model.parent_id == parent_id
        ).order_by(self.model.order_num).all()
    
    def get_menu_list(
        self,
        db: Session, 
        *, 
        menu_name: Optional[str] = None, 
        status: Optional[str] = None
    ) -> List[Menu]:
        """
        获取菜单列表
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if menu_name:
            query = query.filter(self.model.menu_name.like(f"%{menu_name}%"))
        if status:
            query = query.filter(self.model.status == status)
            
        # 排序
        query = query.order_by(self.model.parent_id, self.model.order_num)
        
        return query.all()
    
    def get_menus_by_role_id(self, db: Session, role_id: int) -> List[Menu]:
        """
        获取指定角色ID的所有菜单
        """
        return db.query(self.model).join(
            role_menu, role_menu.c.menu_id == self.model.menu_id
        ).filter(
            role_menu.c.role_id == role_id
        ).order_by(self.model.parent_id, self.model.order_num).all()
    
    def get_router_tree(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        is_admin: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取菜单路由树
        """
        # 如果是管理员，获取所有可见的菜单
        if is_admin:
            menus = db.query(self.model).filter(
                self.model.status == "0",  # 状态正常的菜单
                self.model.visible == "0"  # 可见的菜单
            ).order_by(self.model.parent_id, self.model.order_num).all()
        else:
            # 获取用户角色关联的菜单
            menus = db.query(self.model).join(
                role_menu, role_menu.c.menu_id == self.model.menu_id
            ).join(
                "roles", "users"  # 通过关系名进行连接
            ).filter(
                self.model.status == "0",  # 状态正常的菜单
                self.model.visible == "0",  # 可见的菜单
                "users.user_id" == user_id  # 用户ID
            ).order_by(self.model.parent_id, self.model.order_num).all()
        
        # 构建菜单树
        return self.build_menu_tree(menus)
    
    def build_menu_tree(self, menus: List[Menu], parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        构建菜单树
        """
        tree = []
        for menu in [m for m in menus if m.parent_id == parent_id]:
            # 只处理目录和菜单类型
            if menu.menu_type in ["M", "C"]:
                menu_dict = {
                    "name": menu.menu_name,
                    "path": menu.path,
                    "hidden": menu.visible == "1",
                    "component": menu.component if menu.component else ("Layout" if menu.parent_id == 0 else ""),
                    "meta": {
                        "title": menu.menu_name,
                        "icon": menu.icon,
                        "noCache": menu.is_cache == 1
                    }
                }
                
                # 处理子菜单
                children = self.build_menu_tree(menus, menu.menu_id)
                if children:
                    menu_dict["children"] = children
                    
                tree.append(menu_dict)
                
        return tree
    
    def get_menu_permission_tree(self, db: Session) -> List[Dict[str, Any]]:
        """
        获取菜单权限树
        """
        # 获取所有菜单
        menus = db.query(self.model).order_by(
            self.model.parent_id, self.model.order_num
        ).all()
        
        # 构建菜单树
        return self.build_permission_tree(menus)
    
    def build_permission_tree(self, menus: List[Menu], parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        构建菜单权限树
        """
        tree = []
        for menu in [m for m in menus if m.parent_id == parent_id]:
            menu_dict = {
                "id": menu.menu_id,
                "label": menu.menu_name,
                "menuName": menu.menu_name,
                "menuType": menu.menu_type,
                "perms": menu.perms,
                "path": menu.path,
                "component": menu.component,
                "icon": menu.icon,
                "visible": menu.visible,
                "status": menu.status,
                "isFrame": menu.is_frame,
                "parentId": menu.parent_id,
                "orderNum": menu.order_num,
            }
            
            # 处理子菜单
            children = self.build_permission_tree(menus, menu.menu_id)
            if children:
                menu_dict["children"] = children
                
            tree.append(menu_dict)
                
        return tree
    
    def has_children(self, db: Session, menu_id: int) -> bool:
        """
        检查菜单是否有子菜单
        """
        return db.query(self.model).filter(
            self.model.parent_id == menu_id
        ).count() > 0


menu = CRUDMenu(Menu) 