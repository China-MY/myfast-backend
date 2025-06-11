from typing import Any

from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import SysUser
from app.schemas.common import ResponseModel
from app.service.online import online_service

router = APIRouter()


@router.post("", response_model=ResponseModel, summary="退出登录", description="用户退出系统登录")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
) -> Any:
    """
    退出登录接口
    """
    # 获取请求头中的Authorization
    auth_header = request.headers.get("Authorization", "")
    token = ""
    
    # 从Authorization头中提取token
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # 去除"Bearer "前缀
    
    if token:
        # 从Redis中移除在线用户记录
        print(f"[DEBUG] 用户退出登录: 用户ID={current_user.user_id}, 用户名={current_user.username}, Token={token[:10]}...")
        online_service.remove_online_user(token)
    else:
        print(f"[WARN] 用户退出登录但未找到Token: 用户ID={current_user.user_id}, 用户名={current_user.username}")
    
    return ResponseModel(msg="退出成功") 