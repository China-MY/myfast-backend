from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.common.security import create_access_token
from app.config.settings import settings
from app.db.session import get_db
from app.domain.repositories.user import user_repository
from app.domain.schemas.user import User, UserCreate, Token, UserLogin

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: UserLogin = None,
    form: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    用户登录
    
    Args:
        db: 数据库会话
        form_data: 用户登录信息，前端JSON格式提交
        form: OAuth2表单提交，用于swagger测试
        
    Returns:
        访问令牌
    """
    # 使用form_data或form
    username = form_data.username if form_data else form.username
    password = form_data.password if form_data else form.password
    
    # 用户认证
    user = user_repository.authenticate(db, username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.user_id, expires_delta=access_token_expires
    )
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    用户注册
    
    Args:
        db: 数据库会话
        user_in: 用户注册信息
        
    Returns:
        注册用户信息
    """
    # 检查用户是否存在
    user = user_repository.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 创建用户
    user = user_repository.create(db, user_in=user_in)
    
    return user 