from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.system.user import user
from app.models.system.user import SysUser
from app.schemas.system.user import User, UserUpdate
from app.schemas.utils.common import ResponseModel

router = APIRouter()


@router.get("/", response_model=ResponseModel[User])
def read_user_me(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取当前用户信息
    """
    # 重新查询以确保关联数据加载
    user_obj = db.query(SysUser).filter(SysUser.user_id == current_user.user_id).first()
    
    return ResponseModel(
        data=user_obj
    )


@router.put("/", response_model=ResponseModel[User])
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    更新当前用户信息
    """
    # 用户名不允许修改
    if user_in.username and user_in.username != current_user.username:
        raise HTTPException(
            status_code=400,
            detail="不允许修改用户名"
        )
    
    # 使用current_user查询信息而不是db.query，确保返回的信息完整
    user_obj = db.query(SysUser).filter(SysUser.user_id == current_user.user_id).first()
    
    # 更新用户信息
    user_obj = user.update(db, db_obj=user_obj, obj_in=user_in)
    
    return ResponseModel(
        data=user_obj,
        msg="用户信息更新成功"
    )


@router.put("/update-password", response_model=ResponseModel)
def update_password(
    *,
    db: Session = Depends(get_db),
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    更新当前用户密码
    """
    # 验证当前密码
    if not user.authenticate(
        db, username=current_user.username, password=current_password
    ):
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    # 更新密码
    user_obj = db.query(SysUser).filter(SysUser.user_id == current_user.user_id).first()
    user.update(db, db_obj=user_obj, obj_in={"password": new_password})
    
    return ResponseModel(
        msg="密码更新成功"
    ) 