from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import SysUser
from app.crud.user import user
from app.schemas.token import TokenPayload
from app.service.online import online_service, ONLINE_KEY_PREFIX
from app.core.redis import redis_client
import json


# 创建OAuth2PasswordBearer依赖项
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request = None,
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> SysUser:
    """
    获取当前用户
    """
    try:
        # 解析JWT令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 根据令牌中的用户ID获取用户
    user_id = int(token_data.sub)
    user_obj = db.query(SysUser).filter(SysUser.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    
    # 尝试更新在线用户的最后访问时间
    try:
        key = f"{ONLINE_KEY_PREFIX}{token}"
        if redis_client.exists(key):
            # 获取当前用户信息
            user_data = redis_client.get(key)
            if user_data:
                user_info = json.loads(user_data)
                # 更新最后访问时间
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_info["last_access_time"] = current_time
                
                # 如果有请求信息，更新IP地址
                if request and hasattr(request, "client") and request.client:
                    user_info["ipaddr"] = request.client.host
                
                # 重新保存到Redis，并重置过期时间
                redis_client.setex(
                    key,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    json.dumps(user_info)
                )
    except Exception as e:
        # 更新在线状态失败不应影响正常业务逻辑
        print(f"[WARN] 更新在线用户状态失败: {str(e)}")
    
    return user_obj


def get_current_active_user(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """
    获取当前活跃用户
    """
    if current_user.status != "0":
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user


def check_permissions(required_permissions: list):
    """
    检查用户是否拥有指定的权限
    """
    def permission_dependency(
        db: Session = Depends(get_db), 
        current_user: SysUser = Depends(get_current_active_user)
    ) -> bool:
        # 获取用户权限
        user_permissions = user.get_user_permissions(current_user)
        
        # 超级管理员拥有所有权限
        if "*:*:*" in user_permissions:
            return True
        
        # 检查是否拥有所需权限
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有足够的权限执行此操作",
                )
        
        return True
    
    return permission_dependency 