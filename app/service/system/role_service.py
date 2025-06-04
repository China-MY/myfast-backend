from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.entity.sys_role import SysRole
from app.entity.sys_menu import SysMenu
from app.entity.sys_dept import SysDept
from app.schema.role import RoleCreate, RoleUpdate
from app.common.exception import BusinessException
from app.common.constants import StatusEnum, DeleteFlagEnum

class RoleService:
    """角色服务类"""
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[SysRole]:
        """根据角色ID获取角色信息"""
        return db.query(SysRole).filter(
            SysRole.role_id == role_id,
            SysRole.del_flag == DeleteFlagEnum.NORMAL
        ).first()
    
    @staticmethod
    def get_role_by_key(db: Session, role_key: str) -> Optional[SysRole]:
        """根据角色权限字符获取角色信息"""
        return db.query(SysRole).filter(
            SysRole.role_key == role_key,
            SysRole.del_flag == DeleteFlagEnum.NORMAL
        ).first()
    
    @staticmethod
    def get_roles(
        db: Session, 
        page_num: int = 1, 
        page_size: int = 10,
        role_name: Optional[str] = None,
        role_key: Optional[str] = None,
        status: Optional[str] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取角色列表"""
        query = db.query(SysRole).filter(SysRole.del_flag == DeleteFlagEnum.NORMAL)
        
        # 应用过滤条件
        if role_name:
            query = query.filter(SysRole.role_name.like(f"%{role_name}%"))
        if role_key:
            query = query.filter(SysRole.role_key.like(f"%{role_key}%"))
        if status:
            query = query.filter(SysRole.status == status)
        if begin_time and end_time:
            query = query.filter(SysRole.create_time.between(begin_time, end_time))
        
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(SysRole.role_sort).offset((page_num - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items,
            "page_num": page_num,
            "page_size": page_size
        }
    
    @staticmethod
    def create_role(db: Session, role_in: RoleCreate, current_user_name: str) -> SysRole:
        """创建角色"""
        # 检查角色名称是否已存在
        exist_role = db.query(SysRole).filter(
            SysRole.role_name == role_in.role_name,
            SysRole.del_flag == DeleteFlagEnum.NORMAL
        ).first()
        if exist_role:
            raise BusinessException(code=400, msg=f"角色名称 {role_in.role_name} 已存在")
        
        # 检查角色权限字符是否已存在
        exist_role = db.query(SysRole).filter(
            SysRole.role_key == role_in.role_key,
            SysRole.del_flag == DeleteFlagEnum.NORMAL
        ).first()
        if exist_role:
            raise BusinessException(code=400, msg=f"角色权限字符 {role_in.role_key} 已存在")
        
        # 创建角色对象
        role_data = role_in.dict(exclude={"menu_ids", "dept_ids"})
        role_data["create_by"] = current_user_name
        role_data["create_time"] = datetime.now()
        
        db_role = SysRole(**role_data)
        
        # 处理菜单关系
        if role_in.menu_ids:
            menus = db.query(SysMenu).filter(
                SysMenu.menu_id.in_(role_in.menu_ids),
                SysMenu.status == StatusEnum.NORMAL
            ).all()
            db_role.menus = menus
        
        # 处理部门关系
        if role_in.dept_ids:
            depts = db.query(SysDept).filter(
                SysDept.dept_id.in_(role_in.dept_ids),
                SysDept.status == StatusEnum.NORMAL,
                SysDept.del_flag == DeleteFlagEnum.NORMAL
            ).all()
            db_role.depts = depts
        
        # 保存角色
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def update_role(
        db: Session, 
        role: SysRole,
        role_in: Union[RoleUpdate, Dict[str, Any]],
        current_user_name: str
    ) -> SysRole:
        """更新角色"""
        role_data = role_in.dict(exclude={"menu_ids", "dept_ids"}) if isinstance(role_in, RoleUpdate) else role_in
        role_data["update_by"] = current_user_name
        role_data["update_time"] = datetime.now()
        
        # 检查角色名称是否已存在
        if "role_name" in role_data and role_data["role_name"] != role.role_name:
            exist_role = db.query(SysRole).filter(
                SysRole.role_name == role_data["role_name"],
                SysRole.del_flag == DeleteFlagEnum.NORMAL,
                SysRole.role_id != role.role_id
            ).first()
            if exist_role:
                raise BusinessException(code=400, msg=f"角色名称 {role_data['role_name']} 已存在")
        
        # 检查角色权限字符是否已存在
        if "role_key" in role_data and role_data["role_key"] != role.role_key:
            exist_role = db.query(SysRole).filter(
                SysRole.role_key == role_data["role_key"],
                SysRole.del_flag == DeleteFlagEnum.NORMAL,
                SysRole.role_id != role.role_id
            ).first()
            if exist_role:
                raise BusinessException(code=400, msg=f"角色权限字符 {role_data['role_key']} 已存在")
        
        # 更新基本信息
        for key, value in role_data.items():
            if hasattr(role, key) and value is not None:
                setattr(role, key, value)
        
        # 处理菜单关系
        if isinstance(role_in, RoleUpdate) and role_in.menu_ids is not None:
            menus = db.query(SysMenu).filter(
                SysMenu.menu_id.in_(role_in.menu_ids),
                SysMenu.status == StatusEnum.NORMAL
            ).all()
            role.menus = menus
        
        # 处理部门关系
        if isinstance(role_in, RoleUpdate) and role_in.dept_ids is not None:
            depts = db.query(SysDept).filter(
                SysDept.dept_id.in_(role_in.dept_ids),
                SysDept.status == StatusEnum.NORMAL,
                SysDept.del_flag == DeleteFlagEnum.NORMAL
            ).all()
            role.depts = depts
        
        # 保存角色
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def delete_role(db: Session, role_id: int, current_user_name: str) -> bool:
        """删除角色（逻辑删除）"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            return False
        
        # 不允许删除管理员角色
        if role.role_key == "admin":
            raise BusinessException(code=400, msg="不允许删除管理员角色")
        
        # 检查角色是否已分配用户
        if role.users and len(role.users) > 0:
            raise BusinessException(code=400, msg="该角色已分配用户，不能删除")
        
        # 逻辑删除
        role.del_flag = DeleteFlagEnum.DELETED
        role.update_by = current_user_name
        role.update_time = datetime.now()
        
        db.add(role)
        db.commit()
        return True
    
    @staticmethod
    def update_role_status(
        db: Session, 
        role_id: int, 
        status: str,
        current_user_name: str
    ) -> bool:
        """更新角色状态"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            return False
        
        # 不允许禁用管理员角色
        if status == StatusEnum.DISABLE and role.role_key == "admin":
            raise BusinessException(code=400, msg="不允许禁用管理员角色")
        
        # 更新状态
        role.status = status
        role.update_by = current_user_name
        role.update_time = datetime.now()
        
        db.add(role)
        db.commit()
        return True
    
    @staticmethod
    def get_role_menu_ids(db: Session, role_id: int) -> List[int]:
        """获取角色菜单ID列表"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            return []
        
        return [menu.menu_id for menu in role.menus]
    
    @staticmethod
    def get_role_dept_ids(db: Session, role_id: int) -> List[int]:
        """获取角色部门ID列表"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            return []
        
        return [dept.dept_id for dept in role.depts] 