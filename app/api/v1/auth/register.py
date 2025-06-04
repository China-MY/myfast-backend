from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.crud.user import user
from app.schemas.user import UserCreate, User
from app.schemas.common import ResponseModel

router = APIRouter()


@router.post("", response_model=ResponseModel[User])
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    # 检查用户名是否已存在
    if user.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证邮箱是否已存在
    if user_in.email and db.query(user.model).filter(user.model.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    # 验证手机号是否已存在
    if user_in.phonenumber and db.query(user.model).filter(user.model.phonenumber == user_in.phonenumber).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被使用"
        )

    # 设置默认值
    if not user_in.dept_id:
        user_in.dept_id = 100  # 默认部门
    
    # 默认普通用户角色
    if not user_in.role_ids:
        user_in.role_ids = [2]  # 普通角色ID
    
    # 创建用户
    user_obj = user.create(db, obj_in=user_in)
    
    return ResponseModel[User](
        data=user_obj,
        msg="用户注册成功"
    ) 