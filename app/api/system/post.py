from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.system.post import SysPost
from app.domain.schemas.system.post import PostCreate, PostUpdate, PostInfo, PostQuery
from app.common.response import success, error, page
from app.service.system.post_service import (
    get_post, get_posts, create_post, update_post, delete_post
)

router = APIRouter()


@router.get("/list", summary="获取岗位列表")
async def get_post_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: PostQuery = Depends(),
):
    """
    获取岗位列表（分页查询）
    """
    try:
        posts, total = get_posts(db, params)
        post_list = [
            {
                "post_id": post.post_id,
                "post_code": post.post_code,
                "post_name": post.post_name,
                "post_sort": post.post_sort,
                "status": post.status,
                "create_time": post.create_time,
                "remark": post.remark
            }
            for post in posts
        ]
        return page(rows=post_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{post_id}", summary="获取岗位详情")
async def get_post_info(
    post_id: int = Path(..., description="岗位ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取岗位详情
    """
    try:
        post = get_post(db, post_id)
        if not post:
            return error(msg="岗位不存在", code=404)
        post_info = {
            "post_id": post.post_id,
            "post_code": post.post_code,
            "post_name": post.post_name,
            "post_sort": post.post_sort,
            "status": post.status,
            "create_time": post.create_time,
            "remark": post.remark
        }
        return success(data=post_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加岗位")
async def add_post(
    post_data: PostCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加岗位
    """
    try:
        post = create_post(db, post_data)
        return success(msg="岗位添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改岗位")
async def edit_post(
    post_data: PostUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改岗位
    """
    try:
        post = update_post(db, post_data.post_id, post_data)
        return success(msg="岗位修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{post_id}", summary="删除岗位")
async def remove_post(
    post_id: int = Path(..., description="岗位ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除岗位
    """
    try:
        result = delete_post(db, post_id)
        return success(msg="岗位删除成功")
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 