from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.entity.sys_menu import SysMenu
from app.common.constants import StatusEnum, VisibleEnum, MenuTypeEnum
from app.common.exception import BusinessException

class MenuService:
    """菜单服务类"""
    
    @staticmethod
    def get_menu_by_id(db: Session, menu_id: int) -> Optional[SysMenu]:
        """根据菜单ID获取菜单信息"""
        return db.query(SysMenu).filter(SysMenu.menu_id == menu_id).first()
    
    @staticmethod
    def get_menus(
        db: Session,
        menu_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[SysMenu]:
        """获取菜单列表"""
        query = db.query(SysMenu)
        
        # 应用过滤条件
        if menu_name:
            query = query.filter(SysMenu.menu_name.like(f"%{menu_name}%"))
        if status:
            query = query.filter(SysMenu.status == status)
        
        # 按照父菜单ID和排序字段排序
        query = query.order_by(SysMenu.parent_id, SysMenu.order_num)
        
        return query.all()
    
    @staticmethod
    def create_menu(
        db: Session, 
        menu_data: Dict[str, Any],
        current_user_name: str
    ) -> SysMenu:
        """创建菜单"""
        # 验证父菜单
        if menu_data.get("parent_id") and menu_data.get("parent_id") != 0:
            parent_menu = MenuService.get_menu_by_id(db, menu_data["parent_id"])
            if not parent_menu:
                raise BusinessException(code=400, msg="父菜单不存在")
            
            # 如果父菜单是按钮，则不允许创建子菜单
            if parent_menu.menu_type == MenuTypeEnum.BUTTON:
                raise BusinessException(code=400, msg="不能在按钮菜单下创建子菜单")
        
        # 设置创建信息
        menu_data["create_by"] = current_user_name
        menu_data["create_time"] = datetime.now()
        
        # 创建菜单
        menu = SysMenu(**menu_data)
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu
    
    @staticmethod
    def update_menu(
        db: Session, 
        menu: SysMenu,
        menu_data: Dict[str, Any],
        current_user_name: str
    ) -> SysMenu:
        """更新菜单"""
        # 不能将菜单的父ID设置为自己或其子菜单的ID
        if "parent_id" in menu_data and menu_data["parent_id"] != 0:
            if menu_data["parent_id"] == menu.menu_id:
                raise BusinessException(code=400, msg="父菜单不能选择自己")
            
            # 检查是否选择了子菜单作为父菜单
            children = MenuService.get_child_menus(db, menu.menu_id)
            child_ids = [child.menu_id for child in children]
            if menu_data["parent_id"] in child_ids:
                raise BusinessException(code=400, msg="父菜单不能选择子菜单")
            
            # 验证父菜单是否存在
            parent_menu = MenuService.get_menu_by_id(db, menu_data["parent_id"])
            if not parent_menu:
                raise BusinessException(code=400, msg="父菜单不存在")
            
            # 如果父菜单是按钮，则不允许设置
            if parent_menu.menu_type == MenuTypeEnum.BUTTON:
                raise BusinessException(code=400, msg="不能选择按钮作为父菜单")
        
        # 设置更新信息
        menu_data["update_by"] = current_user_name
        menu_data["update_time"] = datetime.now()
        
        # 更新菜单信息
        for key, value in menu_data.items():
            if hasattr(menu, key) and value is not None:
                setattr(menu, key, value)
        
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu
    
    @staticmethod
    def delete_menu(db: Session, menu_id: int) -> bool:
        """删除菜单"""
        menu = MenuService.get_menu_by_id(db, menu_id)
        if not menu:
            return False
        
        # 检查是否有子菜单
        children = MenuService.get_child_menus(db, menu_id)
        if children:
            raise BusinessException(code=400, msg="存在子菜单，不允许删除")
        
        # 检查菜单是否已分配角色
        if menu.roles and len(menu.roles) > 0:
            raise BusinessException(code=400, msg="菜单已分配角色，不允许删除")
        
        # 删除菜单
        db.delete(menu)
        db.commit()
        return True
    
    @staticmethod
    def get_child_menus(db: Session, parent_id: int) -> List[SysMenu]:
        """获取子菜单列表"""
        return db.query(SysMenu).filter(SysMenu.parent_id == parent_id).all()
    
    @staticmethod
    def build_menu_tree(menus: List[SysMenu], parent_id: int = 0) -> List[Dict[str, Any]]:
        """构建菜单树"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                menu_dict = {
                    "menu_id": menu.menu_id,
                    "menu_name": menu.menu_name,
                    "parent_id": menu.parent_id,
                    "order_num": menu.order_num,
                    "path": menu.path,
                    "component": menu.component,
                    "query": menu.query,
                    "is_frame": menu.is_frame,
                    "is_cache": menu.is_cache,
                    "menu_type": menu.menu_type,
                    "visible": menu.visible,
                    "status": menu.status,
                    "perms": menu.perms,
                    "icon": menu.icon,
                    "create_time": menu.create_time,
                    "children": MenuService.build_menu_tree(menus, menu.menu_id)
                }
                tree.append(menu_dict)
        return tree
    
    @staticmethod
    def get_menu_tree(db: Session) -> List[Dict[str, Any]]:
        """获取菜单树"""
        menus = db.query(SysMenu).filter(
            SysMenu.status == StatusEnum.NORMAL,
            SysMenu.visible == VisibleEnum.SHOW
        ).order_by(SysMenu.parent_id, SysMenu.order_num).all()
        
        return MenuService.build_menu_tree(menus) 