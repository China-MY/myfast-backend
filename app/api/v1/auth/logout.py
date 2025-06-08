from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import SysUser
from app.schemas.common import ResponseModel

router = APIRouter()


@router.post("/logout", response_model=ResponseModel, summary="用户注销", description="注销当前用户的登录状态")
def logout(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    用户注销接口
    
    该接口会使当前登录用户的会话失效
    注意: 由于JWT令牌无法在服务端强制失效，完整的注销应由前端配合实现
    前端应在调用此接口后：
    1. 清除本地存储的令牌
    2. 重定向到登录页面
    
    返回:
    - 注销成功的响应
    """
    # 记录注销操作
    # 这里可以添加后续的审计日志记录、更新用户状态等操作
    
    return ResponseModel(
        code=200,
        msg="注销成功"
    ) 