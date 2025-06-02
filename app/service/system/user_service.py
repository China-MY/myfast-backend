from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.user import SysUser
from app.domain.models.system.user_role import SysUserRole
from app.domain.models.system.user_post import SysUserPost
from app.domain.schemas.system.user import UserCreate, UserUpdate, UserInfo, UserQuery
from app.core.security import get_password_hash, verify_password
from app.common.exception import NotFound


def get_user(db: Session, user_id: int) -> Optional[SysUser]:
    """
    根据用户ID获取用户信息
    """
    return db.query(SysUser).filter(
        SysUser.user_id == user_id,
        SysUser.del_flag == "0"
    ).first()


def get_user_by_username(db: Session, username: str) -> Optional[SysUser]:
    """
    根据用户名获取用户信息
    """
    return db.query(SysUser).filter(
        SysUser.username == username,
        SysUser.del_flag == "0"
    ).first()


def get_users(
    db: Session, 
    params: UserQuery
) -> Tuple[List[SysUser], int]:
    """
    获取用户列表（分页查询）
    """
    query = db.query(SysUser).filter(SysUser.del_flag == "0")
    
    # 构建查询条件
    if params.username:
        query = query.filter(SysUser.username.like(f"%{params.username}%"))
    if params.nickname:
        query = query.filter(SysUser.nickname.like(f"%{params.nickname}%"))
    if params.status:
        query = query.filter(SysUser.status == params.status)
    if params.dept_id:
        query = query.filter(SysUser.dept_id == params.dept_id)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysUser.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    users = query.order_by(SysUser.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return users, total


def create_user(
    db: Session, 
    user_data: UserCreate
) -> SysUser:
    """
    创建用户
    """
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
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


def update_user(
    db: Session, 
    user_id: int, 
    user_data: UserUpdate
) -> Optional[SysUser]:
    """
    更新用户信息
    """
    # 获取用户信息
    db_user = get_user(db, user_id)
    if not db_user:
        raise NotFound(f"用户ID {user_id} 不存在")
    
    # 检查用户名是否已存在（如果修改了用户名）
    if db_user.username != user_data.username and get_user_by_username(db, user_data.username):
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


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户（逻辑删除）
    """
    # 获取用户信息
    db_user = get_user(db, user_id)
    if not db_user:
        raise NotFound(f"用户ID {user_id} 不存在")
    
    # 逻辑删除
    db_user.del_flag = "2"
    db.commit()
    
    return True


def reset_password(
    db: Session, 
    user_id: int, 
    new_password: str
) -> bool:
    """
    重置用户密码
    """
    # 获取用户信息
    db_user = get_user(db, user_id)
    if not db_user:
        raise NotFound(f"用户ID {user_id} 不存在")
    
    # 更新密码
    db_user.password = get_password_hash(new_password)
    db.commit()
    
    return True 