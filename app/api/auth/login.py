from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import verify_password, create_access_token
from app.config import settings
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.user import LoginRequest, LoginResponse
from app.common.response import success, error

router = APIRouter()


@router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    用户登录接口
    """
    # 查询用户
    user = db.query(SysUser).filter(
        SysUser.username == form_data.username,
        SysUser.del_flag == "0"
    ).first()
    
    # 验证用户存在和密码正确
    if not user or not verify_password(form_data.password, user.password):
        return error(msg="用户名或密码错误", code=401)
    
    # 验证用户状态
    if user.status != "0":
        return error(msg="用户已被禁用", code=403)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.user_id, 
        expires_delta=access_token_expires
    )
    
    # 返回令牌
    return success(data={
        "token": access_token,
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }) 