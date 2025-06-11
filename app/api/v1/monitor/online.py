from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.schemas.online import OnlineUserOut, ForceLogoutParams
from app.schemas.common import ResponseModel, PageResponseModel
from app.service.online import online_service

router = APIRouter()


@router.get("/list", response_model=PageResponseModel[List[OnlineUserOut]], summary="获取在线用户列表", description="分页获取在线用户列表")
def list_online_users(
    db: Session = Depends(get_db),
    *,
    ipaddr: Optional[str] = None,
    username: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["monitor:online:list"]))
) -> Any:
    """
    获取在线用户列表
    """
    skip = (page - 1) * page_size
    online_users, total = online_service.get_online_users(
        db,
        skip=skip, 
        limit=page_size,
        ipaddr=ipaddr,
        username=username
    )
    
    return PageResponseModel[List[OnlineUserOut]](
        data=online_users,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/{token}", response_model=ResponseModel, summary="强制退出登录", description="强制用户退出登录")
def force_logout(
    *,
    db: Session = Depends(get_db),
    token: str,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["monitor:online:forceLogout"]))
) -> Any:
    """
    强制用户退出登录
    """
    # 不能踢出自己
    if online_service.is_current_user_token(token, current_user):
        raise HTTPException(status_code=400, detail="不能踢出自己")
    
    # 执行强制退出
    success = online_service.force_logout(db, token=token)
    if not success:
        raise HTTPException(status_code=404, detail="用户不在线或令牌无效")
    
    return ResponseModel(msg="强制退出成功")


@router.post("/batchLogout", response_model=ResponseModel, summary="批量强制退出", description="批量强制用户退出登录")
def batch_force_logout(
    *,
    db: Session = Depends(get_db),
    params: ForceLogoutParams,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["monitor:online:batchForceLogout"]))
) -> Any:
    """
    批量强制用户退出登录
    """
    # 过滤掉当前用户自己的token
    tokens = [token for token in params.session_ids if not online_service.is_current_user_token(token, current_user)]
    
    if not tokens:
        raise HTTPException(status_code=400, detail="不能批量踢出自己或无效的令牌列表")
    
    # 执行批量强制退出
    count = online_service.batch_force_logout(db, tokens=tokens)
    
    return ResponseModel(data={"count": count}, msg=f"已强制退出{count}个用户") 