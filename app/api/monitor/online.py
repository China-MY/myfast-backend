from typing import List
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.monitor.online_user import OnlineUserQuery
from app.common.response import success, error, page
from app.service.monitor.online_service import (
    get_online_user, get_online_users, delete_online_user,
    clean_expired_online_users
)

router = APIRouter()


@router.get("/list", summary="获取在线用户列表")
async def get_online_user_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: OnlineUserQuery = Depends(),
):
    """
    获取在线用户列表（分页查询）
    """
    try:
        # 清理过期的在线用户
        clean_expired_online_users(db)
        
        # 查询在线用户
        online_users, total = get_online_users(db, params)
        
        # 转换为前端格式
        user_list = [
            {
                "id": user.id,
                "token_id": user.token_id,
                "user_id": user.user_id,
                "username": user.username,
                "dept_name": user.dept_name,
                "login_ip": user.login_ip,
                "login_location": user.login_location,
                "browser": user.browser,
                "os": user.os,
                "login_time": user.login_time,
                "last_access_time": user.last_access_time,
                "expire_time": user.expire_time
            }
            for user in online_users
        ]
        
        return page(rows=user_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{online_id}", summary="强制退出在线用户")
async def force_logout(
    online_id: int = Path(..., description="在线用户ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    强制退出在线用户
    """
    try:
        # 获取在线用户信息
        online_user = get_online_user(db, online_id)
        if not online_user:
            return error(msg="在线用户不存在", code=404)
        
        # 不能强退自己
        if online_user.user_id == current_user.user_id:
            return error(msg="不能强制退出自己", code=400)
        
        # 删除在线用户
        result = delete_online_user(db, online_id)
        
        return success(msg="强制退出成功")
    except Exception as e:
        return error(msg=str(e))


@router.delete("/batchLogout", summary="批量强制退出")
async def batch_logout(
    online_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    批量强制退出在线用户
    """
    try:
        # 当前用户ID
        current_id = current_user.user_id
        
        # 批量删除
        success_count = 0
        for online_id in online_ids:
            # 获取在线用户信息
            online_user = get_online_user(db, online_id)
            if not online_user:
                continue
            
            # 不能强退自己
            if online_user.user_id == current_id:
                continue
            
            # 删除在线用户
            result = delete_online_user(db, online_id)
            if result:
                success_count += 1
        
        return success(msg=f"批量强制退出成功，共退出 {success_count} 个用户")
    except Exception as e:
        return error(msg=str(e)) 