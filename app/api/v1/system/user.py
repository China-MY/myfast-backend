from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.crud.user import user
from app.models.user import SysUser
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.common import ResponseModel, PageResponseModel, PageInfo

router = APIRouter()


@router.get("/", response_model=PageResponseModel[User])
def read_users(
    db: Session = Depends(get_db),
    username: str = Query(None, description="用户名"),
    nickname: str = Query(None, description="用户昵称"),
    status: str = Query(None, description="状态"),
    dept_id: int = Query(None, description="部门ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页记录数"),
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:list"]))
) -> Any:
    """
    获取用户列表
    """
    # 构建查询条件
    query = db.query(SysUser)
    if username:
        query = query.filter(SysUser.username.like(f"%{username}%"))
    if nickname:
        query = query.filter(SysUser.nickname.like(f"%{nickname}%"))
    if status:
        query = query.filter(SysUser.status == status)
    if dept_id:
        query = query.filter(SysUser.dept_id == dept_id)
    
    # 统计总数
    total = query.count()
    
    # 分页
    users = query.offset((page - 1) * pageSize).limit(pageSize).all()
    
    # 构建响应
    return PageResponseModel[User](
        rows=users,
        pageInfo=PageInfo(
            page=page,
            pageSize=pageSize,
            total=total
        )
    )


@router.post("/", response_model=ResponseModel[User])
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:add"]))
) -> Any:
    """
    创建新用户
    """
    # 检查用户名是否已存在
    if user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user_obj = user.create(db, obj_in=user_in)
    
    return ResponseModel[User](
        data=user_obj,
        msg="用户创建成功"
    )


@router.get("/{user_id}", response_model=ResponseModel[User])
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., description="用户ID"),
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:query"]))
) -> Any:
    """
    获取指定用户信息
    """
    # 获取用户
    user_obj = db.query(SysUser).filter(SysUser.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return ResponseModel[User](
        data=user_obj
    )


@router.put("/{user_id}", response_model=ResponseModel[User])
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., description="用户ID"),
    user_in: UserUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:edit"]))
) -> Any:
    """
    更新用户信息
    """
    # 获取用户
    user_obj = db.query(SysUser).filter(SysUser.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 如果更新用户名，检查是否已存在
    if user_in.username and user_in.username != user_obj.username:
        if user.get_by_username(db, username=user_in.username):
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 不允许更新管理员用户
    if user_obj.username == "admin" and current_user.username != "admin":
        raise HTTPException(status_code=400, detail="不允许修改超级管理员")
    
    # 更新用户
    user_obj = user.update(db, db_obj=user_obj, obj_in=user_in)
    
    return ResponseModel[User](
        data=user_obj,
        msg="用户更新成功"
    )


@router.delete("/{user_id}", response_model=ResponseModel)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., description="用户ID"),
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:remove"]))
) -> Any:
    """
    删除用户
    """
    # 获取用户
    user_obj = db.query(SysUser).filter(SysUser.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许删除管理员用户
    if user_obj.username == "admin":
        raise HTTPException(status_code=400, detail="不允许删除超级管理员")
    
    # 不允许删除自己
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="不允许删除当前登录用户")
    
    # 删除用户
    db.delete(user_obj)
    db.commit()
    
    return ResponseModel(
        msg="用户删除成功"
    )


@router.put("/{user_id}/reset-password", response_model=ResponseModel)
def reset_password(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., description="用户ID"),
    password: str = Body(..., embed=True),
    current_user: SysUser = Depends(get_current_active_user),
    has_permission: bool = Depends(check_permissions(["system:user:resetPwd"]))
) -> Any:
    """
    重置用户密码
    """
    # 获取用户
    user_obj = db.query(SysUser).filter(SysUser.user_id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许重置管理员密码（除非是管理员本人）
    if user_obj.username == "admin" and current_user.username != "admin":
        raise HTTPException(status_code=400, detail="不允许修改超级管理员密码")
    
    # 更新密码
    user.update(db, db_obj=user_obj, obj_in={"password": password})
    
    return ResponseModel(
        msg="密码重置成功"
    ) 