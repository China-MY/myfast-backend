from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.crud.utils.base import CRUDBase
from app.models.system.user import SysUser
from app.models.system.role import SysRole
from app.models.system.post import SysPost
from app.schemas.system.user import UserCreate, UserUpdate
from app.utils.password import get_password_hash, verify_password


class CRUDUser(CRUDBase[SysUser, UserCreate, UserUpdate]):
    """用户CRUD操作类"""
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[SysUser]:
        """
        根据用户名获取用户
        :param db: 数据库会话
        :param username: 用户名
        :return: 用户对象
        """
        return db.query(SysUser).filter(SysUser.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> SysUser:
        """
        创建新用户
        :param db: 数据库会话
        :param obj_in: 用户创建数据
        :return: 创建的用户
        """
        db_obj = SysUser(
            username=obj_in.username,
            nickname=obj_in.nickname,
            email=obj_in.email,
            phonenumber=obj_in.phonenumber,
            sex=obj_in.sex,
            status=obj_in.status,
            dept_id=obj_in.dept_id,
            password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 添加角色关联
        if obj_in.role_ids:
            roles = db.query(SysRole).filter(SysRole.role_id.in_(obj_in.role_ids)).all()
            db_obj.roles = roles
            db.commit()
            
        # 添加岗位关联
        if obj_in.post_ids:
            posts = db.query(SysPost).filter(SysPost.post_id.in_(obj_in.post_ids)).all()
            db_obj.posts = posts
            db.commit()
            
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysUser, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> SysUser:
        """
        更新用户
        :param db: 数据库会话
        :param db_obj: 数据库中的用户对象
        :param obj_in: 更新数据
        :return: 更新后的用户
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 如果更新密码，则哈希处理
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
        
        # 角色处理
        role_ids = None
        if "role_ids" in update_data:
            role_ids = update_data.pop("role_ids", None)
            
        # 岗位处理
        post_ids = None
        if "post_ids" in update_data:
            post_ids = update_data.pop("post_ids", None)
        
        # 调用父类方法完成更新
        result = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        # 更新角色关系
        if role_ids is not None:
            roles = db.query(SysRole).filter(SysRole.role_id.in_(role_ids)).all()
            result.roles = roles
            db.commit()
            
        # 更新岗位关系
        if post_ids is not None:
            posts = db.query(SysPost).filter(SysPost.post_id.in_(post_ids)).all()
            result.posts = posts
            db.commit()
            
        db.refresh(result)
        return result
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[SysUser]:
        """
        验证用户
        :param db: 数据库会话
        :param username: 用户名
        :param password: 密码
        :return: 验证通过返回用户，否则返回None
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    def is_active(self, user: SysUser) -> bool:
        """
        判断用户是否处于活动状态
        :param user: 用户对象
        :return: 是否处于活动状态
        """
        return user.status == "0"
    
    def is_deleted(self, user: SysUser) -> bool:
        """
        判断用户是否已被删除
        :param user: 用户对象
        :return: 是否已被删除
        """
        return user.del_flag != "0"
    
    def get_user_permissions(self, user: SysUser) -> List[str]:
        """
        获取用户权限集合
        :param user: 用户对象
        :return: 权限列表
        """
        perms = set()
        # 管理员拥有所有权限
        admin_role = any(role.role_key == "admin" for role in user.roles)
        if admin_role:
            perms.add("*:*:*")
        else:
            for role in user.roles:
                if role.status == "0":  # 角色启用状态
                    for menu in role.menus:
                        if menu.status == "0" and menu.perms:  # 菜单启用且有权限标识
                            perms.add(menu.perms)
        
        return list(perms)


user = CRUDUser(SysUser) 