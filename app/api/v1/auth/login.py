from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.crud.user import user
from app.models.user import SysUser
from app.schemas.token import Token
from app.schemas.user import UserLogin, UserInfo, User
from app.schemas.common import ResponseModel
from app.utils.jwt import create_access_token

router = APIRouter()


@router.post("/login", response_model=ResponseModel[Token], summary="OAuth2标准登录", description="使用OAuth2标准方式登录系统，获取访问令牌")
def login_access_token(
    request: Request,
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2标准登录接口
    
    - **form_data**: OAuth2表单数据，包含用户名和密码
    
    返回:
    - **token**: 访问令牌信息
    """
    # 验证用户
    user_obj = user.authenticate(db, username=form_data.username, password=form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active(user_obj):
        raise HTTPException(status_code=400, detail="用户未激活")
    
    # 更新登录信息
    login_ip = request.client.host if request.client else ""
    db.query(SysUser).filter(SysUser.user_id == user_obj.user_id).update({
        "login_ip": login_ip,
        "login_date": datetime.now()
    })
    db.commit()
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user_obj.user_id), expires_delta=access_token_expires
    )
    
    return ResponseModel[Token](
        code=200,
        msg="登录成功",
        data=Token(
            access_token=token,
            token_type="bearer"
        )
    )


@router.post("/login/account", response_model=ResponseModel[Token], summary="账号密码登录", description="使用账号和密码登录系统，获取访问令牌")
def login_by_account(
    request: Request,
    login: UserLogin, 
    db: Session = Depends(get_db)
) -> Any:
    """
    账号密码登录接口
    
    - **login**: 登录信息，包含用户名和密码
    
    返回:
    - **token**: 访问令牌信息
    """
    # 验证用户
    user_obj = user.authenticate(db, username=login.username, password=login.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    if not user.is_active(user_obj):
        raise HTTPException(status_code=400, detail="用户未激活")
    
    # 更新登录信息
    login_ip = request.client.host if request.client else ""
    db.query(SysUser).filter(SysUser.user_id == user_obj.user_id).update({
        "login_ip": login_ip,
        "login_date": datetime.now()
    })
    db.commit()
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user_obj.user_id), expires_delta=access_token_expires
    )
    
    return ResponseModel[Token](
        code=200,
        msg="登录成功",
        data=Token(
            access_token=token,
            token_type="bearer"
        )
    )


@router.get("/info", response_model=ResponseModel[UserInfo], summary="获取用户信息", description="获取当前登录用户的详细信息、角色和权限")
def get_user_info(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取当前登录用户信息
    
    返回:
    - **user**: 用户基本信息
    - **roles**: 用户角色列表
    - **permissions**: 用户权限列表
    """
    # 重新查询用户以确保关联数据加载
    user_obj = db.query(SysUser).filter(SysUser.user_id == current_user.user_id).first()
    
    # 获取用户权限
    permissions = user.get_user_permissions(user_obj)
    
    # 获取角色标识
    roles = [role.role_key for role in user_obj.roles if role.status == "0"]
    
    return ResponseModel[UserInfo](
        data=UserInfo(
            user=user_obj,
            roles=roles,
            permissions=permissions
        )
    ) 