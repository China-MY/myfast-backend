from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.menu import SysMenu
from app.domain.models.system.role_menu import SysRoleMenu
from app.domain.schemas.system.menu import MenuCreate, MenuUpdate, MenuInfo, MenuTreeNode
from app.common.constants import MenuType
from app.common.exception import NotFound

from fastapi import HTTPException, status
from app.crud.menu import menu as menu_crud
from app.models.menu import Menu
from app.schemas.menu import RouterVo


def get_menu(db: Session, menu_id: int) -> Optional[SysMenu]:
    """
    根据菜单ID获取菜单信息
    """
    return db.query(SysMenu).filter(SysMenu.menu_id == menu_id).first()


def get_menu_by_perms(db: Session, perms: str) -> Optional[SysMenu]:
    """
    根据权限标识获取菜单信息
    """
    return db.query(SysMenu).filter(SysMenu.perms == perms).first()


def get_menus(db: Session) -> List[SysMenu]:
    """
    获取所有菜单列表
    """
    return db.query(SysMenu).order_by(
        SysMenu.parent_id.asc(), 
        SysMenu.order_num.asc()
    ).all()


def get_menus_by_user_id(db: Session, user_id: int) -> List[SysMenu]:
    """
    根据用户ID获取菜单列表
    """
    # 如果是管理员，直接返回所有菜单
    if user_id == 1:
        return get_menus(db)
    
    # 查询用户所属角色的菜单
    menus = db.query(SysMenu).join(
        SysRoleMenu, SysRoleMenu.c.menu_id == SysMenu.menu_id
    ).join(
        "sys_user_role", SysRoleMenu.c.role_id == "sys_user_role".c.role_id
    ).filter(
        "sys_user_role".c.user_id == user_id,
        SysMenu.status == "0"
    ).order_by(
        SysMenu.parent_id.asc(), 
        SysMenu.order_num.asc()
    ).all()
    
    return menus


def create_menu(db: Session, menu_data: MenuCreate) -> SysMenu:
    """
    创建菜单
    """
    # 检查权限标识是否已存在
    if menu_data.perms and get_menu_by_perms(db, menu_data.perms):
        raise ValueError(f"权限标识 {menu_data.perms} 已存在")
    
    # 创建菜单对象
    db_menu = SysMenu(**menu_data.dict())
    
    # 保存菜单信息
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    return db_menu


def update_menu(db: Session, menu_id: int, menu_data: MenuUpdate) -> Optional[SysMenu]:
    """
    更新菜单信息
    """
    # 获取菜单信息
    db_menu = get_menu(db, menu_id)
    if not db_menu:
        raise NotFound(f"菜单ID {menu_id} 不存在")
    
    # 不能将菜单的父ID设置为自己
    if menu_data.parent_id == menu_id:
        raise ValueError("父菜单不能选择自己")
    
    # 检查权限标识是否已存在（如果修改了权限标识）
    if menu_data.perms and db_menu.perms != menu_data.perms and get_menu_by_perms(db, menu_data.perms):
        raise ValueError(f"权限标识 {menu_data.perms} 已存在")
    
    # 检查是否存在子菜单（如果修改了菜单类型且不是目录）
    if db_menu.menu_type == MenuType.DIRECTORY and menu_data.menu_type != MenuType.DIRECTORY:
        child_count = db.query(SysMenu).filter(SysMenu.parent_id == menu_id).count()
        if child_count > 0:
            raise ValueError("存在子菜单，不允许修改菜单类型")
    
    # 更新菜单基本信息
    for key, value in menu_data.dict(exclude={"menu_id"}).items():
        setattr(db_menu, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_menu)
    
    return db_menu


def delete_menu(db: Session, menu_id: int) -> bool:
    """
    删除菜单
    """
    # 获取菜单信息
    db_menu = get_menu(db, menu_id)
    if not db_menu:
        raise NotFound(f"菜单ID {menu_id} 不存在")
    
    # 检查是否存在子菜单
    child_count = db.query(SysMenu).filter(SysMenu.parent_id == menu_id).count()
    if child_count > 0:
        raise ValueError("存在子菜单，不允许删除")
    
    # 检查是否存在角色关联
    role_count = db.execute(
        SysRoleMenu.select().where(
            SysRoleMenu.c.menu_id == menu_id
        )
    ).rowcount
    
    if role_count > 0:
        raise ValueError("菜单已分配角色，不允许删除")
    
    # 删除菜单
    db.delete(db_menu)
    db.commit()
    
    return True


def build_menu_tree(menus: List[SysMenu], parent_id: int = 0) -> List[Dict[str, Any]]:
    """
    构建菜单树
    """
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            node = {
                "menu_id": menu.menu_id,
                "parent_id": menu.parent_id,
                "menu_name": menu.menu_name,
                "path": menu.path,
                "component": menu.component,
                "query": menu.query,
                "visible": menu.visible,
                "status": menu.status,
                "perms": menu.perms,
                "is_frame": menu.is_frame,
                "is_cache": menu.is_cache,
                "menu_type": menu.menu_type,
                "icon": menu.icon,
                "order_num": menu.order_num,
                "create_time": menu.create_time,
                "children": build_menu_tree(menus, menu.menu_id)
            }
            tree.append(node)
    return tree


def build_menu_tree_select(menus: List[SysMenu], parent_id: int = 0) -> List[Dict[str, Any]]:
    """
    构建菜单树选择项
    """
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            node = {
                "id": menu.menu_id,
                "label": menu.menu_name,
                "children": build_menu_tree_select(menus, menu.menu_id)
            }
            # 如果没有子节点，则移除children属性
            if not node["children"]:
                del node["children"]
            tree.append(node)
    return tree


def build_router_tree(menus: List[SysMenu], parent_id: int = 0) -> List[Dict[str, Any]]:
    """
    构建前端路由所需的菜单树
    """
    routers = []
    for menu in menus:
        if menu.parent_id == parent_id and menu.menu_type in [MenuType.DIRECTORY, MenuType.MENU] and menu.status == "0":
            router = {
                "name": menu.path.capitalize() if menu.path else "",
                "path": menu.path,
                "hidden": menu.visible == "1",
                "redirect": "noRedirect" if menu.menu_type == MenuType.DIRECTORY else "",
                "component": menu.component if menu.component else ("Layout" if menu.parent_id == 0 else "ParentView"),
                "query": menu.query,
                "meta": {
                    "title": menu.menu_name,
                    "icon": menu.icon,
                    "noCache": menu.is_cache == 1
                }
            }
            
            # 获取子菜单
            children = build_router_tree(menus, menu.menu_id)
            if children:
                router["children"] = children
            
            routers.append(router)
    
    return routers 


class MenuService:
    @staticmethod
    def get_menu_by_id(db: Session, menu_id: int) -> Optional[Menu]:
        """获取菜单信息"""
        menu = menu_crud.get_by_id(db, menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        return menu

    @staticmethod
    def get_menu_list(
        db: Session,
        menu_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Menu]:
        """获取菜单列表"""
        return menu_crud.get_menu_list(db, menu_name=menu_name, status=status)

    @staticmethod
    def create_menu(db: Session, menu_in: MenuCreate) -> Menu:
        """创建菜单"""
        # 检查父菜单是否存在
        if menu_in.parent_id != 0:
            parent_menu = menu_crud.get_by_id(db, menu_in.parent_id)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"父菜单ID {menu_in.parent_id} 不存在"
                )
            
            # 如果父菜单是按钮，则不能添加子菜单
            if parent_menu.menu_type == "F":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能在按钮下添加子菜单"
                )
        
        # 验证菜单名称在同级菜单下的唯一性
        if menu_crud.get_by_name(db, menu_name=menu_in.menu_name, parent_id=menu_in.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"菜单名称 {menu_in.menu_name} 已存在"
            )
            
        # 创建菜单
        return menu_crud.create(db, obj_in=menu_in)

    @staticmethod
    def update_menu(db: Session, menu_id: int, menu_in: MenuUpdate) -> Menu:
        """更新菜单"""
        # 检查菜单是否存在
        db_menu = menu_crud.get_by_id(db, menu_id)
        if not db_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        # 不能将菜单的父ID设置为自己或其子菜单ID
        if menu_in.parent_id and menu_in.parent_id != 0 and menu_in.parent_id != db_menu.parent_id:
            # 检查是否是自己
            if menu_in.parent_id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父菜单不能选择自己"
                )
                
            # 检查是否是自己的子菜单
            child_menus = menu_crud.get_children_by_parent_id(db, menu_id)
            child_ids = [menu.menu_id for menu in child_menus]
            if menu_in.parent_id in child_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父菜单不能设置为子菜单"
                )
                
            # 检查父菜单是否存在
            parent_menu = menu_crud.get_by_id(db, menu_in.parent_id)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"父菜单ID {menu_in.parent_id} 不存在"
                )
                
            # 如果父菜单是按钮，则不能作为父菜单
            if parent_menu.menu_type == "F":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能在按钮下添加子菜单"
                )
        
        # 验证菜单名称在同级菜单下的唯一性
        if menu_in.menu_name and menu_in.menu_name != db_menu.menu_name:
            parent_id = menu_in.parent_id if menu_in.parent_id is not None else db_menu.parent_id
            if menu_crud.get_by_name(db, menu_name=menu_in.menu_name, parent_id=parent_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"菜单名称 {menu_in.menu_name} 已存在"
                )
                
        # 更新菜单
        return menu_crud.update(db, db_obj=db_menu, obj_in=menu_in)

    @staticmethod
    def delete_menu(db: Session, menu_id: int) -> None:
        """删除菜单"""
        # 检查菜单是否存在
        db_menu = menu_crud.get_by_id(db, menu_id)
        if not db_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
            
        # 检查是否有子菜单
        if menu_crud.has_children(db, menu_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="存在子菜单,不允许删除"
            )
            
        # 删除菜单
        menu_crud.remove(db, id=menu_id)

    @staticmethod
    def get_router_tree(db: Session, user_id: int, is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取路由树"""
        # 获取菜单路由树
        return menu_crud.get_router_tree(db, user_id=user_id, is_admin=is_admin)

    @staticmethod
    def get_menu_permission_tree(db: Session) -> List[Dict[str, Any]]:
        """获取菜单权限树"""
        return menu_crud.get_menu_permission_tree(db)

    @staticmethod
    def get_menu_tree_select(db: Session) -> List[Dict[str, Any]]:
        """获取菜单下拉树"""
        # 获取所有菜单
        menus = menu_crud.get_menu_list(db)
        
        # 构建菜单树
        return MenuService._build_tree_select(menus)
    
    @staticmethod
    def _build_tree_select(menus: List[Menu], parent_id: int = 0) -> List[Dict[str, Any]]:
        """构建菜单下拉树"""
        tree = []
        for menu in [m for m in menus if m.parent_id == parent_id]:
            menu_dict = {
                "id": menu.menu_id,
                "label": menu.menu_name,
            }
            
            # 处理子菜单
            children = MenuService._build_tree_select(menus, menu.menu_id)
            if children:
                menu_dict["children"] = children
                
            tree.append(menu_dict)
                
        return tree

    @staticmethod
    def get_role_menu_tree_select(db: Session, role_id: int) -> Dict[str, Any]:
        """获取角色的菜单树选择数据"""
        # 获取所有菜单
        menus = menu_crud.get_menu_list(db)
        
        # 构建菜单树
        menu_tree = MenuService._build_tree_select(menus)
        
        # 获取角色菜单ID列表
        checked_keys = menu_crud.get_role_menu_ids(db, role_id)
        
        return {
            "menus": menu_tree,
            "checkedKeys": checked_keys
        }
        

menu_service = MenuService() 