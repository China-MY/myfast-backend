from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.monitor.online_user import SysUserOnline
from app.domain.schemas.monitor.online_user import OnlineUserCreate, OnlineUserQuery
from app.common.exception import NotFound


def get_online_user(db: Session, id: int) -> Optional[SysUserOnline]:
    """
    根据会话ID获取在线用户信息
    """
    return db.query(SysUserOnline).filter(SysUserOnline.id == id).first()


def get_online_user_by_token(db: Session, token_id: str) -> Optional[SysUserOnline]:
    """
    根据token获取在线用户信息
    """
    return db.query(SysUserOnline).filter(SysUserOnline.token_id == token_id).first()


def get_online_users(
    db: Session, 
    params: OnlineUserQuery
) -> Tuple[List[SysUserOnline], int]:
    """
    获取在线用户列表（分页查询）
    """
    query = db.query(SysUserOnline)
    
    # 构建查询条件
    if params.username:
        query = query.filter(SysUserOnline.username.like(f"%{params.username}%"))
    if params.ip_address:
        query = query.filter(SysUserOnline.login_ip.like(f"%{params.ip_address}%"))
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    online_users = query.order_by(SysUserOnline.last_access_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return online_users, total


def create_online_user(db: Session, online_user_data: OnlineUserCreate) -> SysUserOnline:
    """
    创建在线用户记录
    """
    # 检查是否已存在相同token的记录
    existing_user = get_online_user_by_token(db, online_user_data.token_id)
    if existing_user:
        # 更新最后访问时间
        existing_user.last_access_time = datetime.now()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # 创建在线用户对象
    db_online_user = SysUserOnline(**online_user_data.dict())
    
    # 保存在线用户信息
    db.add(db_online_user)
    db.commit()
    db.refresh(db_online_user)
    
    return db_online_user


def delete_online_user(db: Session, id: int) -> bool:
    """
    删除在线用户记录
    """
    # 获取在线用户信息
    db_online_user = get_online_user(db, id)
    if not db_online_user:
        raise NotFound(f"在线用户ID {id} 不存在")
    
    # 删除在线用户
    db.delete(db_online_user)
    db.commit()
    
    return True


def delete_online_user_by_token(db: Session, token_id: str) -> bool:
    """
    根据token删除在线用户记录
    """
    # 获取在线用户信息
    db_online_user = get_online_user_by_token(db, token_id)
    if not db_online_user:
        return False
    
    # 删除在线用户
    db.delete(db_online_user)
    db.commit()
    
    return True


def clean_expired_online_users(db: Session) -> int:
    """
    清理过期的在线用户记录
    """
    # 获取当前时间
    now = datetime.now()
    
    # 查询过期的在线用户
    expired_users = db.query(SysUserOnline).filter(
        SysUserOnline.expire_time < now
    ).all()
    
    # 批量删除
    count = 0
    for user in expired_users:
        db.delete(user)
        count += 1
    
    db.commit()
    
    return count


def update_last_access_time(db: Session, token_id: str) -> bool:
    """
    更新用户最后访问时间
    """
    # 获取在线用户信息
    db_online_user = get_online_user_by_token(db, token_id)
    if not db_online_user:
        return False
    
    # 更新最后访问时间
    db_online_user.last_access_time = datetime.now()
    db.commit()
    
    return True 