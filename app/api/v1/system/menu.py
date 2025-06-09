from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.models.menu import SysMenu
from app.schemas.menu import MenuCreate, MenuUpdate, MenuOut, MenuTree
from app.schemas.common import ResponseModel
from app.crud.menu import menu as menu_crud

router = APIRouter()


@router.get("", response_model=ResponseModel[List[MenuOut]], summary="获取菜单列表", description="获取所有菜单列表")
def list_menus(
    db: Session = Depends(get_db),
    *,
    menu_name: Optional[str] = None,
    status: Optional[str] = None,
    _: bool = Depends(check_permissions(["system:menu:list"]))
) -> Any:
    """
    获取菜单列表
    """
    menus = menu_crud.get_all_with_filter(
        db, 
        menu_name=menu_name,
        status=status
    )
    
    return ResponseModel[List[MenuOut]](data=menus)


@router.get("/tree", response_model=ResponseModel[List[MenuTree]], summary="获取菜单树", description="获取菜单树结构")
def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取菜单树结构
    """
    menus = menu_crud.get_tree(db)
    return ResponseModel[List[MenuTree]](data=menus)


@router.get("/user", response_model=ResponseModel[List[MenuTree]], summary="获取用户菜单", description="获取当前用户可访问的菜单")
def get_user_menus(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取当前用户可访问的菜单
    """
    menu_list = menu_crud.get_user_menus(db, user=current_user)
    return ResponseModel[List[MenuTree]](data=menu_list)


@router.get("/{menu_id}", response_model=ResponseModel[MenuOut], summary="获取菜单详情", description="根据菜单ID获取菜单详情")
def get_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    _: bool = Depends(check_permissions(["system:menu:query"]))
) -> Any:
    """
    获取菜单详情
    """
    menu_obj = menu_crud.get(db, id=menu_id)
    if not menu_obj:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    return ResponseModel[MenuOut](data=menu_obj)


@router.post("", response_model=ResponseModel[MenuOut], summary="创建菜单", description="创建新菜单")
def create_menu(
    *,
    db: Session = Depends(get_db),
    menu_in: MenuCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:menu:add"]))
) -> Any:
    """
    创建新菜单
    """
    # 检查父菜单是否存在
    if menu_in.parent_id and menu_in.parent_id != 0:
        parent = menu_crud.get(db, id=menu_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父菜单不存在")
    
    menu_obj = menu_crud.create(db, obj_in=menu_in, creator_id=current_user.user_id)
    return ResponseModel[MenuOut](data=menu_obj, msg="创建成功")


@router.put("/{menu_id}", response_model=ResponseModel[MenuOut], summary="更新菜单", description="更新菜单信息")
def update_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    menu_in: MenuUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:menu:edit"]))
) -> Any:
    """
    更新菜单信息
    """
    menu_obj = menu_crud.get(db, id=menu_id)
    if not menu_obj:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 检查父菜单是否存在
    if menu_in.parent_id and menu_in.parent_id != 0:
        parent = menu_crud.get(db, id=menu_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父菜单不存在")
        
        # 不能将自己设为自己的父菜单
        if menu_in.parent_id == menu_id:
            raise HTTPException(status_code=400, detail="不能选择自己作为父菜单")
        
        # 不能将自己的子菜单设为自己的父菜单
        if menu_crud.is_child(db, parent_id=menu_id, child_id=menu_in.parent_id):
            raise HTTPException(status_code=400, detail="不能选择子菜单作为父菜单")
    
    menu_obj = menu_crud.update(db, db_obj=menu_obj, obj_in=menu_in, updater_id=current_user.user_id)
    return ResponseModel[MenuOut](data=menu_obj, msg="更新成功")


@router.delete("/{menu_id}", response_model=ResponseModel, summary="删除菜单", description="删除指定菜单")
def delete_menu(
    *,
    db: Session = Depends(get_db),
    menu_id: int,
    _: bool = Depends(check_permissions(["system:menu:remove"]))
) -> Any:
    """
    删除菜单
    """
    menu_obj = menu_crud.get(db, id=menu_id)
    if not menu_obj:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 检查是否有子菜单
    if menu_crud.has_children(db, menu_id=menu_id):
        raise HTTPException(status_code=400, detail="存在子菜单，不能删除")
    
    menu_crud.remove(db, id=menu_id)
    return ResponseModel(msg="删除成功")


@router.get("/role/{role_id}", response_model=None, summary="获取角色菜单", description="获取角色关联的菜单列表")
def get_role_menus(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    _: bool = Depends(check_permissions(["system:menu:list"]))
) -> Any:
    """
    获取角色关联的菜单列表
    """
    print(f"[API] 获取角色菜单: role_id={role_id}")
    
    try:
        # 获取角色的菜单ID列表
        menu_ids = menu_crud.get_role_menu_ids(db, role_id=role_id)
        
        # 获取所有菜单
        menus = menu_crud.get_all_with_filter(db, status="0")
        
        # 构建菜单树
        menu_tree = menu_crud._build_menu_tree(menus)
        
        # 返回标准响应格式
        response = {
            "code": 200,
            "msg": "操作成功",
            "data": menu_tree
        }
        
        print(f"[API] 角色菜单树响应完成，树节点数: {len(menu_tree)}")
        
        return response
    except Exception as e:
        print(f"[API ERROR] 获取角色菜单异常: {str(e)}")
        
        response = {
            "code": 500,
            "msg": f"获取角色菜单失败: {str(e)}",
            "data": []
        }
        
        return response 