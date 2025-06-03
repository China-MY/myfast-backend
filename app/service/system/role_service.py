from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.role import SysRole
from app.domain.models.system.role_menu import SysRoleMenu
from app.domain.models.system.role_dept import SysRoleDept
from app.domain.models.system.user_role import SysUserRole
from app.domain.schemas.system.role import RoleCreate, RoleUpdate, RoleInfo, RoleQuery
from app.common.exception import NotFound

from fastapi import HTTPException, status
from app.crud.role import role as role_crud
from app.models.role import Role
from app.schemas.role import RoleMenuTree


def get_role(db: Session, role_id: int) -> Optional[SysRole]:
    """
    根据角色ID获取角色信息
    """
    return db.query(SysRole).filter(
        SysRole.role_id == role_id,
        SysRole.del_flag == "0"
    ).first()


def get_role_by_key(db: Session, role_key: str) -> Optional[SysRole]:
    """
    根据角色权限字符串获取角色信息
    """
    return db.query(SysRole).filter(
        SysRole.role_key == role_key,
        SysRole.del_flag == "0"
    ).first()


def get_roles(
    db: Session, 
    params: RoleQuery
) -> Tuple[List[SysRole], int]:
    """
    获取角色列表（分页查询）
    """
    query = db.query(SysRole).filter(SysRole.del_flag == "0")
    
    # 构建查询条件
    if params.role_name:
        query = query.filter(SysRole.role_name.like(f"%{params.role_name}%"))
    if params.role_key:
        query = query.filter(SysRole.role_key.like(f"%{params.role_key}%"))
    if params.status:
        query = query.filter(SysRole.status == params.status)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysRole.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    roles = query.order_by(SysRole.role_sort.asc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return roles, total


def get_role_menu_ids(db: Session, role_id: int) -> List[int]:
    """
    获取角色关联的菜单ID列表
    """
    # 查询角色关联的菜单
    role_menus = db.execute(
        SysRoleMenu.select().where(
            SysRoleMenu.c.role_id == role_id
        )
    ).fetchall()
    
    # 提取菜单ID
    menu_ids = [rm.menu_id for rm in role_menus]
    
    return menu_ids


def get_role_dept_ids(db: Session, role_id: int) -> List[int]:
    """
    获取角色关联的部门ID列表
    """
    # 查询角色关联的部门
    role_depts = db.execute(
        SysRoleDept.select().where(
            SysRoleDept.c.role_id == role_id
        )
    ).fetchall()
    
    # 提取部门ID
    dept_ids = [rd.dept_id for rd in role_depts]
    
    return dept_ids


def create_role(
    db: Session, 
    role_data: RoleCreate
) -> SysRole:
    """
    创建角色
    """
    # 检查角色权限字符串是否已存在
    if get_role_by_key(db, role_data.role_key):
        raise ValueError(f"角色权限字符串 {role_data.role_key} 已存在")
    
    # 创建角色对象
    db_role = SysRole(
        role_name=role_data.role_name,
        role_key=role_data.role_key,
        role_sort=role_data.role_sort,
        data_scope=role_data.data_scope,
        status=role_data.status,
        remark=role_data.remark
    )
    
    # 保存角色信息
    db.add(db_role)
    db.flush()
    
    # 分配菜单权限
    if role_data.menu_ids:
        for menu_id in role_data.menu_ids:
            db.execute(
                SysRoleMenu.insert().values(
                    role_id=db_role.role_id,
                    menu_id=menu_id
                )
            )
    
    # 分配数据权限
    if role_data.dept_ids and role_data.data_scope == "2":  # 自定数据权限
        for dept_id in role_data.dept_ids:
            db.execute(
                SysRoleDept.insert().values(
                    role_id=db_role.role_id,
                    dept_id=dept_id
                )
            )
    
    # 提交事务
    db.commit()
    db.refresh(db_role)
    
    return db_role


def update_role(
    db: Session, 
    role_id: int, 
    role_data: RoleUpdate
) -> Optional[SysRole]:
    """
    更新角色信息
    """
    # 获取角色信息
    db_role = get_role(db, role_id)
    if not db_role:
        raise NotFound(f"角色ID {role_id} 不存在")
    
    # 检查角色权限字符串是否已存在（如果修改了权限字符串）
    if db_role.role_key != role_data.role_key and get_role_by_key(db, role_data.role_key):
        raise ValueError(f"角色权限字符串 {role_data.role_key} 已存在")
    
    # 更新角色基本信息
    for key, value in role_data.dict(exclude={"menu_ids", "dept_ids"}).items():
        if value is not None:
            setattr(db_role, key, value)
    
    # 更新菜单权限
    if role_data.menu_ids is not None:
        # 删除原有菜单关联
        db.execute(
            SysRoleMenu.delete().where(
                SysRoleMenu.c.role_id == role_id
            )
        )
        
        # 添加新的菜单关联
        for menu_id in role_data.menu_ids:
            db.execute(
                SysRoleMenu.insert().values(
                    role_id=role_id,
                    menu_id=menu_id
                )
            )
    
    # 更新数据权限
    if role_data.dept_ids is not None and role_data.data_scope == "2":  # 自定数据权限
        # 删除原有部门关联
        db.execute(
            SysRoleDept.delete().where(
                SysRoleDept.c.role_id == role_id
            )
        )
        
        # 添加新的部门关联
        for dept_id in role_data.dept_ids:
            db.execute(
                SysRoleDept.insert().values(
                    role_id=role_id,
                    dept_id=dept_id
                )
            )
    
    # 提交事务
    db.commit()
    db.refresh(db_role)
    
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    """
    删除角色（逻辑删除）
    """
    # 获取角色信息
    db_role = get_role(db, role_id)
    if not db_role:
        raise NotFound(f"角色ID {role_id} 不存在")
    
    # 检查角色是否已分配
    user_count = db.execute(
        SysUserRole.select().where(
            SysUserRole.c.role_id == role_id
        )
    ).rowcount
    
    if user_count > 0:
        raise ValueError(f"角色已分配，不能删除")
    
    # 逻辑删除
    db_role.del_flag = "1"
    db.commit()
    
    return True


def update_role_status(
    db: Session, 
    role_id: int, 
    status: str
) -> Optional[SysRole]:
    """
    更新角色状态
    """
    # 获取角色信息
    db_role = get_role(db, role_id)
    if not db_role:
        raise NotFound(f"角色ID {role_id} 不存在")
    
    # 更新状态
    db_role.status = status
    db.commit()
    db.refresh(db_role)
    
    return db_role


def get_all_roles(db: Session) -> List[SysRole]:
    """
    获取所有角色列表（不分页）
    """
    return db.query(SysRole).filter(
        SysRole.del_flag == "0"
    ).order_by(SysRole.role_sort.asc()).all()


class RoleService:
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """获取角色信息"""
        role = role_crud.get(db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在"
            )
        return role

    @staticmethod
    def get_role_list(
        db: Session, 
        page: int = 1, 
        page_size: int = 10, 
        role_name: Optional[str] = None,
        role_key: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取角色列表"""
        skip = (page - 1) * page_size
        
        # 获取角色列表
        result = role_crud.get_role_list(
            db, 
            skip=skip, 
            limit=page_size, 
            role_name=role_name,
            role_key=role_key,
            status=status
        )
        
        return result

    @staticmethod
    def create_role(db: Session, role_in: RoleCreate) -> Role:
        """创建角色"""
        # 检查角色名称是否已存在
        if role_crud.get_by_role_name(db, role_name=role_in.role_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色名称 '{role_in.role_name}' 已存在"
            )
        
        # 检查角色权限标识是否已存在
        if role_crud.get_by_role_key(db, role_key=role_in.role_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色权限标识 '{role_in.role_key}' 已存在"
            )
            
        # 创建角色
        return role_crud.create_with_menus(db, obj_in=role_in)

    @staticmethod
    def update_role(db: Session, role_id: int, role_in: RoleUpdate) -> Role:
        """更新角色"""
        db_role = role_crud.get(db, id=role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
            
        # 不允许更新admin角色
        if db_role.role_key == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改超级管理员角色"
            )
            
        # 检查角色名称唯一性
        if role_in.role_name and role_in.role_name != db_role.role_name:
            if role_crud.get_by_role_name(db, role_name=role_in.role_name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色名称 '{role_in.role_name}' 已存在"
                )
                
        # 检查角色权限标识唯一性
        if role_in.role_key and role_in.role_key != db_role.role_key:
            if role_crud.get_by_role_key(db, role_key=role_in.role_key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色权限标识 '{role_in.role_key}' 已存在"
                )
                
        # 更新角色
        return role_crud.update_with_menus(db, db_obj=db_role, obj_in=role_in)

    @staticmethod
    def delete_role(db: Session, role_id: int) -> Role:
        """删除角色"""
        db_role = role_crud.get(db, id=role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
            
        # 不允许删除admin角色
        if db_role.role_key == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除超级管理员角色"
            )
            
        # 逻辑删除角色
        db_role.del_flag = "1"
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    def batch_delete_roles(db: Session, role_ids: List[int]) -> List[Role]:
        """批量删除角色"""
        # 检查是否包含admin角色
        for role_id in role_ids:
            db_role = role_crud.get(db, id=role_id)
            if db_role and db_role.role_key == "admin":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能删除超级管理员角色"
                )
                
        # 批量逻辑删除角色
        deleted_roles = []
        for role_id in role_ids:
            db_role = role_crud.get(db, id=role_id)
            if db_role:
                db_role.del_flag = "1"
                db.add(db_role)
                deleted_roles.append(db_role)
                
        db.commit()
        return deleted_roles

    @staticmethod
    def update_role_status(db: Session, role_id: int, status: str) -> Role:
        """更新角色状态"""
        db_role = role_crud.get(db, id=role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
            
        # 不允许禁用admin角色
        if db_role.role_key == "admin" and status != "0":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用超级管理员角色"
            )
            
        # 更新角色状态
        return role_crud.update_role_status(db, role_id=role_id, status=status)

    @staticmethod
    def get_role_menu_tree(db: Session, role_id: int) -> RoleMenuTree:
        """获取角色菜单权限树"""
        db_role = role_crud.get(db, id=role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
            
        # 获取角色菜单ID列表
        menu_ids = role_crud.get_role_menu_ids(db, role_id)
        
        # 如果是自定义数据权限，获取角色部门ID列表
        dept_ids = None
        if db_role.data_scope == "2":  # 自定义数据权限
            dept_ids = role_crud.get_role_dept_ids(db, role_id)
            
        # 构建角色菜单树
        role_menu_tree = RoleMenuTree(
            role_id=db_role.role_id,
            role_name=db_role.role_name,
            role_key=db_role.role_key,
            data_scope=db_role.data_scope,
            menu_ids=menu_ids,
            dept_ids=dept_ids
        )
        
        return role_menu_tree

    @staticmethod
    def get_all_roles(db: Session, status: Optional[str] = None) -> List[Role]:
        """获取所有角色列表"""
        return role_crud.get_all_roles(db, status=status)


role_service = RoleService() 