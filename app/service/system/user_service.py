from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.service.base_service import BaseService
from app.domain.models.system.user import SysUser
from app.domain.models.system.user_role import SysUserRole
from app.domain.models.system.user_post import SysUserPost
from app.domain.schemas.system.user import UserCreate, UserUpdate, UserInfo, UserQuery
from app.core.security import get_password_hash, verify_password
from app.common.exception import NotFound

from fastapi import HTTPException, status
from app.crud.user import user as user_crud
from app.crud.role import role as role_crud
from app.crud.post import post as post_crud
from app.models.user import User


class UserService(BaseService[SysUser, UserCreate, UserUpdate, UserQuery]):
    """用户服务类"""
    
    def __init__(self):
        super().__init__(SysUser)
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[SysUser]:
        """
        根据用户ID获取用户信息
        """
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.del_flag == "0"
        ).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[SysUser]:
        """
        根据用户名获取用户信息
        """
        return db.query(self.model).filter(
            self.model.username == username,
            self.model.del_flag == "0"
        ).first()
    
    def get_list(
        self, 
        db: Session, 
        params: UserQuery
    ) -> Tuple[List[SysUser], int]:
        """
        获取用户列表（分页查询）
        """
        query = db.query(self.model).filter(self.model.del_flag == "0")
        
        # 构建查询条件
        if params.username:
            query = query.filter(self.model.username.like(f"%{params.username}%"))
        if params.nickname:
            query = query.filter(self.model.nickname.like(f"%{params.nickname}%"))
        if params.status:
            query = query.filter(self.model.status == params.status)
        if params.dept_id:
            query = query.filter(self.model.dept_id == params.dept_id)
        if params.begin_time and params.end_time:
            query = query.filter(
                self.model.create_time.between(params.begin_time, params.end_time)
            )
        
        # 统计总数
        total = query.count()
        
        # 分页查询
        users = query.order_by(self.model.create_time.desc()).offset(
            (params.page_num - 1) * params.page_size
        ).limit(params.page_size).all()
        
        return users, total
    
    def create(self, db: Session, user_data: UserCreate) -> SysUser:
        """
        创建用户
        """
        # 检查用户名是否已存在
        if self.get_by_username(db, user_data.username):
            raise ValueError(f"用户名 {user_data.username} 已存在")
        
        # 创建用户对象
        db_user = SysUser(
            username=user_data.username,
            nickname=user_data.nickname,
            email=user_data.email,
            phonenumber=user_data.phonenumber,
            sex=user_data.sex,
            avatar=user_data.avatar,
            password=get_password_hash(user_data.password),
            status=user_data.status,
            dept_id=user_data.dept_id,
            remark=user_data.remark
        )
        
        # 保存用户信息
        db.add(db_user)
        db.flush()
        
        # 分配角色
        if user_data.role_ids:
            for role_id in user_data.role_ids:
                db.execute(
                    SysUserRole.insert().values(
                        user_id=db_user.user_id,
                        role_id=role_id
                    )
                )
        
        # 分配岗位
        if user_data.post_ids:
            for post_id in user_data.post_ids:
                db.execute(
                    SysUserPost.insert().values(
                        user_id=db_user.user_id,
                        post_id=post_id
                    )
                )
        
        # 提交事务
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def update(
        self,
        db: Session, 
        user_id: int, 
        user_data: UserUpdate
    ) -> Optional[SysUser]:
        """
        更新用户信息
        """
        # 获取用户信息
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            raise NotFound(f"用户ID {user_id} 不存在")
        
        # 检查用户名是否已存在（如果修改了用户名）
        if db_user.username != user_data.username and self.get_by_username(db, user_data.username):
            raise ValueError(f"用户名 {user_data.username} 已存在")
        
        # 更新用户基本信息
        for key, value in user_data.dict(exclude={"password", "role_ids", "post_ids"}).items():
            if value is not None:
                setattr(db_user, key, value)
        
        # 更新密码（如果提供了新密码）
        if user_data.password:
            db_user.password = get_password_hash(user_data.password)
        
        # 更新角色（如果提供了角色列表）
        if user_data.role_ids is not None:
            # 删除原有角色关联
            db.execute(
                SysUserRole.delete().where(
                    SysUserRole.c.user_id == user_id
                )
            )
            
            # 添加新的角色关联
            for role_id in user_data.role_ids:
                db.execute(
                    SysUserRole.insert().values(
                        user_id=user_id,
                        role_id=role_id
                    )
                )
        
        # 更新岗位（如果提供了岗位列表）
        if user_data.post_ids is not None:
            # 删除原有岗位关联
            db.execute(
                SysUserPost.delete().where(
                    SysUserPost.c.user_id == user_id
                )
            )
            
            # 添加新的岗位关联
            for post_id in user_data.post_ids:
                db.execute(
                    SysUserPost.insert().values(
                        user_id=user_id,
                        post_id=post_id
                    )
                )
        
        # 提交事务
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        """
        删除用户（逻辑删除）
        """
        # 获取用户信息
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            raise NotFound(f"用户ID {user_id} 不存在")
        
        # 逻辑删除
        db_user.del_flag = "2"
        db.commit()
        
        return True
    
    def reset_password(
        self,
        db: Session, 
        user_id: int, 
        new_password: str
    ) -> bool:
        """
        重置用户密码
        """
        # 获取用户信息
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            raise NotFound(f"用户ID {user_id} 不存在")
        
        # 更新密码
        db_user.password = get_password_hash(new_password)
        db.commit()
        
        return True


# 创建全局用户服务实例
user_service = UserService()


@staticmethod
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """获取用户信息"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    return user

@staticmethod
def get_user_list(
    db: Session, 
    page: int = 1, 
    page_size: int = 10, 
    username: Optional[str] = None,
    status: Optional[str] = None,
    phonenumber: Optional[str] = None,
    dept_id: Optional[int] = None
) -> Dict[str, Any]:
    """获取用户列表"""
    skip = (page - 1) * page_size
    
    # 获取用户列表
    return user_crud.get_multi_with_info(
        db, 
        skip=skip, 
        limit=page_size, 
        username=username,
        status=status,
        phonenumber=phonenumber,
        dept_id=dept_id
    )

@staticmethod
def create_user(db: Session, user_in: UserCreate) -> User:
    """创建新用户"""
    # 检查用户名是否已存在
    db_user = user_crud.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_in.email:
        db_user = user_crud.get_by_email(db, email=user_in.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
                
    # 创建用户
    return user_crud.create_with_roles_and_posts(db, obj_in=user_in)

@staticmethod
def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
    """更新用户信息"""
    # 获取要更新的用户
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 检查用户名唯一性
    if user_in.username != db_user.username:
        db_user_check = user_crud.get_by_username(db, username=user_in.username)
        if db_user_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
                
    # 检查邮箱唯一性
    if user_in.email and user_in.email != db_user.email:
        db_user_check = user_crud.get_by_email(db, email=user_in.email)
        if db_user_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
                
    # 更新用户
    return user_crud.update_with_roles_and_posts(db, db_obj=db_user, obj_in=user_in)

@staticmethod
def delete_user(db: Session, user_id: int) -> User:
    """删除用户"""
    # 检查用户是否存在
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 不允许删除管理员用户
    if db_user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除管理员用户"
        )
        
    # 删除用户
    return user_crud.remove(db, id=user_id)

@staticmethod
def batch_delete_users(db: Session, user_ids: List[int]) -> List[User]:
    """批量删除用户"""
    # 检查是否包含管理员用户
    admin_user = user_crud.get_by_username(db, username="admin")
    if admin_user and admin_user.user_id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除管理员用户"
        )
        
    # 批量删除用户
    return user_crud.remove_multi(db, ids=user_ids)

@staticmethod
def reset_password(db: Session, user_id: int, password: str) -> User:
    """重置用户密码"""
    # 获取用户
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 更新密码
    hashed_password = get_password_hash(password)
    return user_crud.update(db, db_obj=db_user, obj_in={"password": hashed_password})

@staticmethod
def update_password(db: Session, user_id: int, old_password: str, new_password: str) -> User:
    """用户修改密码"""
    # 获取用户
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 验证旧密码
    if not verify_password(old_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
        
    # 更新密码
    hashed_password = get_password_hash(new_password)
    return user_crud.update(db, db_obj=db_user, obj_in={"password": hashed_password})

@staticmethod
def update_user_status(db: Session, user_id: int, status: str) -> User:
    """修改用户状态"""
    # 获取用户
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 不允许修改管理员用户状态
    if db_user.username == "admin" and status != "0":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用管理员用户"
        )
        
    # 更新状态
    return user_crud.update(db, db_obj=db_user, obj_in={"status": status})

@staticmethod
def get_user_roles(db: Session, user_id: int) -> List[dict]:
    """获取用户角色"""
    # 检查用户是否存在
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 获取用户角色
    roles = user_crud.get_user_roles(db, user_id)
    return [{"role_id": role.role_id, "role_name": role.role_name, "role_key": role.role_key} for role in roles]

@staticmethod
def get_user_posts(db: Session, user_id: int) -> List[dict]:
    """获取用户岗位"""
    # 检查用户是否存在
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 获取用户岗位
    posts = user_crud.get_user_posts(db, user_id)
    return [{"post_id": post.post_id, "post_name": post.post_name, "post_code": post.post_code} for post in posts] 