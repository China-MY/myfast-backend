from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.security import get_password_hash, verify_password
from app.models.system.user import SysUser
from app.models.system.role import SysRole
from app.models.system.post import SysPost
from app.schemas.system.user import UserCreate, UserUpdate
from app.common.exception import BusinessException
from app.common.constants import UserStatusEnum, DeleteFlagEnum

class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[SysUser]:
        """根据用户名获取用户信息"""
        return db.query(SysUser).filter(
            SysUser.username == username,
            SysUser.del_flag == DeleteFlagEnum.NORMAL
        ).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[SysUser]:
        """根据用户ID获取用户信息"""
        return db.query(SysUser).filter(
            SysUser.user_id == user_id,
            SysUser.del_flag == DeleteFlagEnum.NORMAL
        ).first()
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[SysUser]:
        """用户身份验证"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if user.status != UserStatusEnum.NORMAL:
            raise BusinessException(code=400, msg="用户已被停用")
        return user
    
    @staticmethod
    def get_users(
        db: Session, 
        page_num: int = 1, 
        page_size: int = 10,
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        status: Optional[str] = None,
        dept_id: Optional[int] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取用户列表"""
        query = db.query(SysUser).filter(SysUser.del_flag == DeleteFlagEnum.NORMAL)
        
        # 应用过滤条件
        if username:
            query = query.filter(SysUser.username.like(f"%{username}%"))
        if nickname:
            query = query.filter(SysUser.nickname.like(f"%{nickname}%"))
        if status:
            query = query.filter(SysUser.status == status)
        if dept_id:
            query = query.filter(SysUser.dept_id == dept_id)
        if begin_time and end_time:
            query = query.filter(SysUser.create_time.between(begin_time, end_time))
        
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(SysUser.user_id).offset((page_num - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items,
            "page_num": page_num,
            "page_size": page_size
        }
    
    @staticmethod
    def create_user(db: Session, user_in: UserCreate, current_user_name: str) -> SysUser:
        """创建用户"""
        # 检查用户名是否已存在
        if UserService.get_user_by_username(db, user_in.username):
            raise BusinessException(code=400, msg=f"用户名 {user_in.username} 已存在")
        
        # 创建用户对象
        user_data = user_in.dict(exclude={"role_ids", "post_ids"})
        user_data["password"] = get_password_hash(user_data["password"])
        user_data["create_by"] = current_user_name
        user_data["create_time"] = datetime.now()
        
        db_user = SysUser(**user_data)
        
        # 处理角色关系
        if user_in.role_ids:
            roles = db.query(SysRole).filter(
                SysRole.role_id.in_(user_in.role_ids),
                SysRole.status == UserStatusEnum.NORMAL,
                SysRole.del_flag == DeleteFlagEnum.NORMAL
            ).all()
            db_user.roles = roles
            
        # 处理岗位关系
        if user_in.post_ids:
            posts = db.query(SysPost).filter(
                SysPost.post_id.in_(user_in.post_ids),
                SysPost.status == UserStatusEnum.NORMAL
            ).all()
            db_user.posts = posts
        
        # 保存用户
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(
        db: Session, 
        user: SysUser,
        user_in: Union[UserUpdate, Dict[str, Any]],
        current_user_name: str
    ) -> SysUser:
        """更新用户"""
        user_data = user_in.dict(exclude={"role_ids", "post_ids"}) if isinstance(user_in, UserUpdate) else user_in
        user_data["update_by"] = current_user_name
        user_data["update_time"] = datetime.now()
        
        # 更新基本信息
        for key, value in user_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        # 处理角色关系
        if isinstance(user_in, UserUpdate) and user_in.role_ids is not None:
            roles = db.query(SysRole).filter(
                SysRole.role_id.in_(user_in.role_ids),
                SysRole.status == UserStatusEnum.NORMAL,
                SysRole.del_flag == DeleteFlagEnum.NORMAL
            ).all()
            user.roles = roles
            
        # 处理岗位关系
        if isinstance(user_in, UserUpdate) and user_in.post_ids is not None:
            posts = db.query(SysPost).filter(
                SysPost.post_id.in_(user_in.post_ids),
                SysPost.status == UserStatusEnum.NORMAL
            ).all()
            user.posts = posts
        
        # 保存用户
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int, current_user_name: str) -> bool:
        """删除用户（逻辑删除）"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # 不允许删除管理员
        for role in user.roles:
            if role.role_key == "admin":
                raise BusinessException(code=400, msg="不允许删除管理员用户")
        
        # 逻辑删除
        user.del_flag = DeleteFlagEnum.DELETED
        user.update_by = current_user_name
        user.update_time = datetime.now()
        
        db.add(user)
        db.commit()
        return True
    
    @staticmethod
    def update_user_password(
        db: Session, 
        user_id: int, 
        new_password: str,
        current_user_name: str
    ) -> bool:
        """更新用户密码"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # 更新密码
        user.password = get_password_hash(new_password)
        user.update_by = current_user_name
        user.update_time = datetime.now()
        
        db.add(user)
        db.commit()
        return True
    
    @staticmethod
    def update_user_status(
        db: Session, 
        user_id: int, 
        status: str,
        current_user_name: str
    ) -> bool:
        """更新用户状态"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # 不允许禁用管理员
        if status == UserStatusEnum.DISABLE:
            for role in user.roles:
                if role.role_key == "admin":
                    raise BusinessException(code=400, msg="不允许禁用管理员用户")
        
        # 更新状态
        user.status = status
        user.update_by = current_user_name
        user.update_time = datetime.now()
        
        db.add(user)
        db.commit()
        return True 