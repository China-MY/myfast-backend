import json
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.core.security import verify_password, create_access_token
from app.config import settings
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.user import LoginRequest, LoginResponse
from app.common.response import success, error

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/tokens", summary="创建访问令牌", response_model=None)
async def create_token(
    login_data: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    创建访问令牌（用户登录）
    """
    username = login_data.get("username")
    password = login_data.get("password")
    
    # 输出调试日志
    logger.info(f"登录尝试: username={username}, 请求数据={login_data}")
    
    if not username or not password:
        logger.warning(f"登录失败: 用户名或密码为空")
        return JSONResponse(
            status_code=400,
            content={"code": 400, "msg": "用户名和密码不能为空", "data": None}
        )
    
    # 查询用户
    user = db.query(SysUser).filter(
        SysUser.username == username,
        SysUser.del_flag == "0"
    ).first()
    
    # 输出调试信息
    if user:
        logger.info(f"找到用户: {username}, 用户ID={user.user_id}, 状态={user.status}")
    else:
        logger.warning(f"用户不存在: {username}")
    
    # 验证用户存在和密码正确
    if not user or not verify_password(password, user.password):
        logger.warning(f"密码验证失败: {username}")
        return JSONResponse(
            status_code=401,
            content={"code": 401, "msg": "用户名或密码错误", "data": None},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证用户状态
    if user.status != "0":
        logger.warning(f"用户已禁用: {username}")
        return JSONResponse(
            status_code=403,
            content={"code": 403, "msg": "用户已被禁用", "data": None}
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.user_id, 
        expires_delta=access_token_expires
    )
    
    logger.info(f"登录成功: {username}")
    
    # 返回令牌
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": access_token,
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
    )


@router.post("/login", summary="用户登录(表单)", response_model=LoginResponse, deprecated=True)
async def login_form(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    用户登录接口(表单方式) - 已废弃，请使用 /api/auth/tokens
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


@router.post("/login/json", summary="用户登录(JSON)", response_model=LoginResponse, deprecated=True)
async def login_json(
    login_data: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    用户登录接口(JSON方式) - 已废弃，请使用 /api/auth/tokens
    """
    username = login_data.get("username")
    password = login_data.get("password")
    
    if not username or not password:
        return error(msg="用户名和密码不能为空", code=400)
    
    # 查询用户
    user = db.query(SysUser).filter(
        SysUser.username == username,
        SysUser.del_flag == "0"
    ).first()
    
    # 验证用户存在和密码正确
    if not user or not verify_password(password, user.password):
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