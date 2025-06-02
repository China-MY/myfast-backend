from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.system.user import UserCreate, UserUpdate, UserInfo, UserQuery
from app.common.response import success, error, page
from app.service.system.user_service import (
    get_user, get_users, create_user, update_user, 
    delete_user, reset_password
)

router = APIRouter()


@router.get("/list", summary="获取用户列表")
async def get_user_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: UserQuery = Depends(),
):
    """
    获取用户列表（分页查询）
    """
    try:
        users, total = get_users(db, params)
        # 这里需要转换为符合前端格式的数据
        user_list = [
            {
                "user_id": user.user_id,
                "username": user.username,
                "nickname": user.nickname,
                "dept_id": user.dept_id,
                "email": user.email,
                "phonenumber": user.phonenumber,
                "status": user.status,
                "create_time": user.create_time,
                # 这里需要处理关联的部门、角色、岗位信息
            }
            for user in users
        ]
        return page(rows=user_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{user_id}", summary="获取用户详情")
async def get_user_info(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取用户详情
    """
    try:
        user = get_user(db, user_id)
        if not user:
            return error(msg="用户不存在", code=404)
        # 这里需要转换为符合前端格式的数据，包含角色、岗位等信息
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "dept_id": user.dept_id,
            "email": user.email,
            "phonenumber": user.phonenumber,
            "sex": user.sex,
            "status": user.status,
            "remark": user.remark,
            "create_time": user.create_time,
            # 这里需要处理关联的部门、角色、岗位信息
            "roles": [],
            "posts": []
        }
        return success(data=user_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加用户")
async def add_user(
    user_data: UserCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加用户
    """
    try:
        user = create_user(db, user_data)
        return success(msg="用户添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改用户")
async def edit_user(
    user_data: UserUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改用户
    """
    try:
        user = update_user(db, user_data.user_id, user_data)
        return success(msg="用户修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{user_id}", summary="删除用户")
async def remove_user(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除用户
    """
    try:
        # 不允许删除自己
        if current_user.user_id == user_id:
            return error(msg="不能删除当前登录用户", code=400)
        
        result = delete_user(db, user_id)
        return success(msg="用户删除成功")
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.put("/resetPwd", summary="重置用户密码")
async def reset_user_password(
    user_id: int = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    重置用户密码
    """
    try:
        result = reset_password(db, user_id, new_password)
        return success(msg="密码重置成功")
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 