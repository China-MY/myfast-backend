from typing import Optional
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.schemas.user import UserCreate
from app.common.security import get_password_hash, verify_password


class UserRepository:
    """用户仓库"""
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        通过用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            用户对象，不存在则返回None
        """
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        """
        创建用户
        
        Args:
            db: 数据库会话
            user_in: 用户创建信息
            
        Returns:
            创建的用户
        """
        # 对密码进行加密
        hashed_password = get_password_hash(user_in.password)
        
        # 创建用户对象
        db_user = User(
            username=user_in.username,
            nickname=user_in.nickname,
            password=hashed_password,
            email=user_in.email,
            phonenumber=user_in.phonenumber,
            sex=user_in.sex,
            dept_id=user_in.dept_id,
            remark=user_in.remark,
            create_by="system",
        )
        
        # 添加到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            
        Returns:
            验证成功返回用户对象，失败返回None
        """
        # 获取用户
        user = self.get_by_username(db, username)
        if not user:
            return None
        
        # 验证密码
        if not verify_password(password, user.password):
            return None
        
        # 验证用户是否激活
        if not user.is_active:
            return None
        
        return user


# 实例化用户仓库
user_repository = UserRepository() 