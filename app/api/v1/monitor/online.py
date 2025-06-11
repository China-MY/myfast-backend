from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.schemas.online import OnlineUserOut, ForceLogoutParams
from app.schemas.common import ResponseModel, PageResponseModel
from app.service.online import online_service

router = APIRouter()


@router.get("/list", summary="获取在线用户列表", description="分页获取在线用户列表")
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
    print(f"[DEBUG] list_online_users API调用 - 参数: ipaddr={ipaddr}, username={username}, page={page}, page_size={page_size}")
    skip = (page - 1) * page_size
    online_users, total = online_service.get_online_users(
        db,
        skip=skip, 
        limit=page_size,
        ipaddr=ipaddr,
        username=username
    )
    
    print(f"[DEBUG] 返回在线用户数量: {len(online_users)}, 总数: {total}")
    
    # 如果返回的用户列表为空但应该有数据，记录警告
    if not online_users and total > 0:
        print("[WARN] 在线用户列表返回空，但总数不为0")
    
    # 将返回的数据转换为纯字典格式，移除datetime对象
    online_users_dict = []
    for user in online_users:
        user_dict = user.model_dump()
        # 转换日期时间字段为字符串
        if isinstance(user_dict.get("start_timestamp"), datetime):
            user_dict["start_timestamp"] = user_dict["start_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(user_dict.get("last_access_time"), datetime):
            user_dict["last_access_time"] = user_dict["last_access_time"].strftime("%Y-%m-%d %H:%M:%S")
        online_users_dict.append(user_dict)
    
    print(f"[DEBUG] 返回前的用户数据: {online_users_dict}")
    
    # 直接返回标准格式，不使用响应模型验证
    return {
        "code": 200,
        "msg": "操作成功",
        "rows": online_users_dict,
        "pageInfo": {
            "page": page,
            "pageSize": page_size,
            "total": total
        }
    }


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