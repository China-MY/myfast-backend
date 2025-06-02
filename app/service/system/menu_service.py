from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.menu import SysMenu
from app.domain.models.system.role_menu import SysRoleMenu
from app.domain.schemas.system.menu import MenuCreate, MenuUpdate, MenuInfo, MenuTreeNode
from app.common.constants import MenuType
from app.common.exception import NotFound


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