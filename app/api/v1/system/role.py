from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.models.role import SysRole
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut, RoleWithMenu
from app.schemas.common import ResponseModel, PageResponseModel
from app.crud.role import role as role_crud

router = APIRouter()


@router.get("/list", response_model=None, summary="获取角色列表", description="分页获取角色列表")
def list_roles(
    db: Session = Depends(get_db),
    *,
    role_name: Optional[str] = None,
    role_key: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["system:role:list"]))
) -> Any:
    """
    获取角色列表
    """
    print(f"[API] 角色列表请求参数: page={page}, page_size={page_size}, role_name={role_name}, role_key={role_key}, status={status}")
    
    skip = (page - 1) * page_size
    roles, total = role_crud.get_multi_with_filter(
        db, 
        skip=skip, 
        limit=page_size,
        role_name=role_name,
        role_key=role_key,
        status=status
    )
    
    print(f"[API] 查询到 {len(roles)} 条角色数据，总数: {total}")
    
    # 确保返回的数据包含必要的字段，特别是前端期望的字段
    role_list = []
    for role in roles:
        role_dict = {
            "role_id": role.role_id,
            "role_name": role.role_name,
            "role_key": role.role_key,
            "role_sort": role.role_sort,
            "status": role.status,
            "create_time": role.create_time,
            "update_time": role.update_time,
            "remark": role.remark
        }
        role_list.append(role_dict)
    
    # 填充响应数据
    response = {
        "code": 200,
        "msg": "操作成功",
        "rows": role_list,  # 前端期望在rows字段中找到角色列表
        "total": total,
        "page": page,
        "page_size": page_size
    }
    
    print(f"[API] 角色列表响应: {response}")
    
    return response


@router.get("/{role_id}", response_model=None, summary="获取角色详情", description="根据角色ID获取角色详情")
def get_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    _: bool = Depends(check_permissions(["system:role:query"]))
) -> Any:
    """
    获取角色详情
    """
    print(f"[API] 获取角色详情: role_id={role_id}")
    role_obj = role_crud.get_by_id(db, role_id=role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        # 获取角色关联的菜单ID列表
        menu_ids = role_crud.get_role_menu_ids(db, role_id=role_id)
        
        # 构造角色详情数据
        role_data = {
            "role_id": role_obj.role_id,
            "role_name": role_obj.role_name,
            "role_key": role_obj.role_key,
            "role_sort": role_obj.role_sort,
            "status": role_obj.status,
            "create_time": role_obj.create_time,
            "update_time": role_obj.update_time,
            "remark": role_obj.remark,
            "menu_ids": menu_ids
        }
        
        # 返回标准响应格式
        response = {
            "code": 200,
            "msg": "操作成功",
            "data": role_data
        }
        
        print(f"[API] 角色详情响应: {response}")
        
        return response
    except Exception as e:
        print(f"[API ERROR] 获取角色详情异常: {str(e)}")
        # 返回错误信息但保留基本角色数据
        role_data = {
            "role_id": role_obj.role_id,
            "role_name": role_obj.role_name,
            "role_key": role_obj.role_key,
            "role_sort": role_obj.role_sort,
            "status": role_obj.status,
            "create_time": role_obj.create_time,
            "update_time": role_obj.update_time,
            "remark": role_obj.remark,
            "menu_ids": []  # 出错时提供空菜单列表
        }
        
        response = {
            "code": 200,  # 仍返回200但带有警告信息
            "msg": f"获取角色详情成功，但菜单数据加载失败: {str(e)}",
            "data": role_data
        }
        
        return response


@router.post("", response_model=ResponseModel[RoleOut], summary="创建角色", description="创建新角色")
def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:role:add"]))
) -> Any:
    """
    创建新角色
    """
    # 检查角色名称和标识是否已存在
    if role_crud.get_by_name(db, role_name=role_in.role_name):
        raise HTTPException(status_code=400, detail="角色名称已存在")
    
    if role_crud.get_by_key(db, role_key=role_in.role_key):
        raise HTTPException(status_code=400, detail="角色标识已存在")
    
    role_obj = role_crud.create(db, obj_in=role_in, creator_id=current_user.user_id)
    
    # 分配菜单权限
    if role_in.menu_ids:
        role_crud.set_role_menus(db, role_id=role_obj.role_id, menu_ids=role_in.menu_ids)
    
    return ResponseModel[RoleOut](data=role_obj, msg="创建成功")


@router.put("/{role_id}", response_model=ResponseModel[RoleOut], summary="更新角色", description="更新角色信息")
def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: RoleUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:role:edit"]))
) -> Any:
    """
    更新角色信息
    """
    role_obj = role_crud.get_by_id(db, role_id=role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查角色名称唯一性
    if role_in.role_name and role_in.role_name != role_obj.role_name:
        if role_crud.get_by_name(db, role_name=role_in.role_name):
            raise HTTPException(status_code=400, detail="角色名称已存在")
    
    # 检查角色标识唯一性
    if role_in.role_key and role_in.role_key != role_obj.role_key:
        if role_crud.get_by_key(db, role_key=role_in.role_key):
            raise HTTPException(status_code=400, detail="角色标识已存在")
    
    role_obj = role_crud.update(db, db_obj=role_obj, obj_in=role_in, updater_id=current_user.user_id)
    
    # 更新菜单权限
    if role_in.menu_ids is not None:
        role_crud.set_role_menus(db, role_id=role_id, menu_ids=role_in.menu_ids)
    
    return ResponseModel[RoleOut](data=role_obj, msg="更新成功")


@router.delete("/{role_id}", response_model=ResponseModel, summary="删除角色", description="删除指定角色")
def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    _: bool = Depends(check_permissions(["system:role:remove"]))
) -> Any:
    """
    删除角色
    """
    role_obj = role_crud.get_by_id(db, role_id=role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查角色是否有关联用户
    if role_crud.has_users(db, role_id=role_id):
        raise HTTPException(status_code=400, detail="角色已分配，不能删除")
    
    role_crud.remove(db, role_id=role_id)
    
    return ResponseModel(msg="删除成功")


@router.get("/select/options", response_model=ResponseModel[List[RoleOut]], summary="获取角色选项", description="获取角色选项列表")
def get_role_options(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取角色选项列表
    """
    roles = role_crud.get_enabled_roles(db)
    return ResponseModel[List[RoleOut]](data=roles) 