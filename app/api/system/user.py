from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.user import UserCreate, UserUpdate, UserInfo, UserQuery
from app.common.response import success, error, page
from app.common.rest import RestApiBase
from app.service.system.user_service import user_service

router = APIRouter()

# 创建RESTful API控制器
user_api = RestApiBase(
    router=router,
    service=user_service,
    prefix="users",
    create_schema=UserCreate,
    update_schema=UserUpdate,
    query_schema=UserQuery,
    tags=["用户管理"],
    id_field="user_id",
    auth_required=True
)

# 添加自定义端点

@router.put("/users/{user_id}/password", summary="重置用户密码")
async def reset_user_password(
    user_id: int = Path(..., description="用户ID"),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    重置用户密码
    """
    try:
        result = user_service.reset_password(db, user_id, new_password)
        return success(msg="密码重置成功")
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))

@router.get("/users/profile", summary="获取当前用户信息")
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取当前登录用户信息
    """
    try:
        user = user_service.get_by_id(db, current_user.user_id)
        if not user:
            return error(msg="用户不存在", code=404)
        
        # 构建用户信息
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "phonenumber": user.phonenumber,
            "sex": user.sex,
            "status": user.status,
            "dept": None,  # 需要关联部门信息
            "roles": [],   # 需要关联角色信息
            "permissions": []  # 需要关联权限信息
        }
        
        return success(data=user_info)
    except Exception as e:
        return error(msg=str(e))

@router.get("/info", summary="获取用户信息")
async def get_user_info(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取当前登录用户信息（前端调用）
    """
    try:
        user = user_service.get_by_id(db, current_user.user_id)
        if not user:
            return error(msg="用户不存在", code=404)
        
        # 构建用户信息
        user_info = {
            "userId": user.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "phonenumber": user.phonenumber,
            "sex": user.sex,
            "status": user.status,
            "roles": ["admin"],   # 临时添加管理员角色
            "permissions": ["*"]  # 临时添加所有权限
        }
        
        return success(data=user_info)
    except Exception as e:
        return error(msg=str(e)) 