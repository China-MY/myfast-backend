from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.role import Role, user_role
from app.models.post import Post, user_post
from app.models.dept import Dept
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        通过用户名获取用户
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        """
        return db.query(User).filter(User.email == email).first()

    def get_multi_with_info(
        self, db: Session, *, skip: int = 0, limit: int = 100, **filters
    ) -> Dict[str, Any]:
        """
        获取用户列表(带部门信息)
        """
        query = db.query(User, Dept.dept_name).outerjoin(
            Dept, User.dept_id == Dept.dept_id
        )
        
        # 应用过滤条件
        for field, value in filters.items():
            if value is not None:
                if field == "dept_id" and value > 0:
                    query = query.filter(User.dept_id == value)
                elif field in ["username", "nickname", "phonenumber", "status"]:
                    if isinstance(value, str) and field != "status":
                        query = query.filter(getattr(User, field).like(f"%{value}%"))
                    else:
                        query = query.filter(getattr(User, field) == value)

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        # 处理结果集
        result_list = []
        for user, dept_name in items:
            user_dict = {
                "user_id": user.user_id,
                "dept_id": user.dept_id,
                "dept_name": dept_name,
                "username": user.username,
                "nickname": user.nickname,
                "email": user.email,
                "phonenumber": user.phonenumber,
                "sex": user.sex,
                "avatar": user.avatar,
                "status": user.status,
                "login_ip": user.login_ip,
                "login_date": user.login_date,
                "create_time": user.create_time,
                "remark": user.remark
            }
            result_list.append(user_dict)
        
        return {"total": total, "items": result_list}

    def create_with_roles_and_posts(
        self, db: Session, *, obj_in: UserCreate
    ) -> User:
        """
        创建用户(同时设置角色和岗位)
        """
        # 创建用户基础信息
        db_obj = User(
            username=obj_in.username,
            nickname=obj_in.nickname,
            email=obj_in.email,
            phonenumber=obj_in.phonenumber,
            sex=obj_in.sex,
            dept_id=obj_in.dept_id,
            status=obj_in.status,
            remark=obj_in.remark,
            password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.flush()
        
        # 设置用户角色关系
        if obj_in.role_ids:
            self.update_user_roles(db, db_obj, obj_in.role_ids)
            
        # 设置用户岗位关系
        if obj_in.post_ids:
            self.update_user_posts(db, db_obj, obj_in.post_ids)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_roles_and_posts(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        更新用户(同时更新角色和岗位)
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 如果更新密码
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
        # 如果不更新密码,从更新数据中删除password字段
        elif "password" in update_data:
            del update_data["password"]
            
        # 处理角色和岗位
        role_ids = update_data.pop("role_ids", None)
        post_ids = update_data.pop("post_ids", None)
        
        # 调用基类的update方法更新基本信息
        user = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        # 更新用户角色关系
        if role_ids is not None:
            self.update_user_roles(db, user, role_ids)
            
        # 更新用户岗位关系
        if post_ids is not None:
            self.update_user_posts(db, user, post_ids)
        
        return user

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        验证用户
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def update_user_roles(self, db: Session, user: User, role_ids: List[int]) -> None:
        """
        更新用户角色关系
        """
        # 先删除用户的所有角色关系
        db.execute(user_role.delete().where(user_role.c.user_id == user.user_id))
        
        # 添加新的角色关系
        for role_id in role_ids:
            db.execute(
                user_role.insert().values(user_id=user.user_id, role_id=role_id)
            )

    def update_user_posts(self, db: Session, user: User, post_ids: List[int]) -> None:
        """
        更新用户岗位关系
        """
        # 先删除用户的所有岗位关系
        db.execute(user_post.delete().where(user_post.c.user_id == user.user_id))
        
        # 添加新的岗位关系
        for post_id in post_ids:
            db.execute(
                user_post.insert().values(user_id=user.user_id, post_id=post_id)
            )
    
    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """
        获取用户的角色列表
        """
        return db.query(Role).join(
            user_role, user_role.c.role_id == Role.role_id
        ).filter(
            user_role.c.user_id == user_id,
            Role.del_flag == "0"
        ).all()
    
    def get_user_posts(self, db: Session, user_id: int) -> List[Post]:
        """
        获取用户的岗位列表
        """
        return db.query(Post).join(
            user_post, user_post.c.post_id == Post.post_id
        ).filter(
            user_post.c.user_id == user_id,
            Post.status == "0"
        ).all()


user = CRUDUser(User) 