from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.system.user import SysUser
from app.schemas.system.post import PostCreate, PostUpdate, PostOut
from app.schemas.utils.common import ResponseModel, PageResponseModel, PageInfo
from app.crud.system.post import post as post_crud

router = APIRouter()


@router.get("/list", response_model=PageResponseModel[PostOut], summary="获取岗位列表", description="分页获取岗位列表")
def list_posts(
    db: Session = Depends(get_db),
    *,
    post_code: Optional[str] = None,
    post_name: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: bool = Depends(check_permissions(["system:post:list"]))
) -> Any:
    """
    获取岗位列表
    """
    try:
        skip = (page - 1) * page_size
        posts, total = post_crud.get_multi_with_filter(
            db, 
            skip=skip, 
            limit=page_size,
            post_code=post_code,
            post_name=post_name,
            status=status
        )
        
        # 转换为Pydantic模型
        post_list = [PostOut.model_validate(post) for post in posts]
        
        return PageResponseModel[PostOut](
            rows=post_list,
            pageInfo=PageInfo(
                page=page,
                pageSize=page_size,
                total=total
            )
        )
    except Exception as e:
        import traceback
        print(f"获取岗位列表出错: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/{post_id}", response_model=ResponseModel[PostOut], summary="获取岗位详情", description="根据岗位ID获取岗位详情")
def get_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    _: bool = Depends(check_permissions(["system:post:query"]))
) -> Any:
    """
    获取岗位详情
    """
    post_obj = post_crud.get_by_id(db, post_id=post_id)
    if not post_obj:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    return ResponseModel[PostOut](data=post_obj)


@router.post("", response_model=ResponseModel[PostOut], summary="创建岗位", description="创建新岗位")
def create_post(
    *,
    db: Session = Depends(get_db),
    post_in: PostCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:post:add"]))
) -> Any:
    """
    创建新岗位
    """
    # 检查岗位编码是否已存在
    if post_crud.get_by_code(db, post_code=post_in.post_code):
        raise HTTPException(status_code=400, detail="岗位编码已存在")
    
    # 检查岗位名称是否已存在
    if post_crud.get_by_name(db, post_name=post_in.post_name):
        raise HTTPException(status_code=400, detail="岗位名称已存在")
    
    post_obj = post_crud.create(db, obj_in=post_in, creator_id=current_user.user_id)
    return ResponseModel[PostOut](data=post_obj, msg="创建成功")


@router.put("/{post_id}", response_model=ResponseModel[PostOut], summary="更新岗位", description="更新岗位信息")
def update_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    post_in: PostUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:post:edit"]))
) -> Any:
    """
    更新岗位信息
    """
    post_obj = post_crud.get_by_id(db, post_id=post_id)
    if not post_obj:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 检查岗位编码唯一性
    if post_in.post_code and post_in.post_code != post_obj.post_code:
        if post_crud.get_by_code(db, post_code=post_in.post_code):
            raise HTTPException(status_code=400, detail="岗位编码已存在")
    
    # 检查岗位名称唯一性
    if post_in.post_name and post_in.post_name != post_obj.post_name:
        if post_crud.get_by_name(db, post_name=post_in.post_name):
            raise HTTPException(status_code=400, detail="岗位名称已存在")
    
    post_obj = post_crud.update(db, db_obj=post_obj, obj_in=post_in, updater_id=current_user.user_id)
    return ResponseModel[PostOut](data=post_obj, msg="更新成功")


@router.delete("/{post_id}", response_model=ResponseModel, summary="删除岗位", description="删除指定岗位")
def delete_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    _: bool = Depends(check_permissions(["system:post:remove"]))
) -> Any:
    """
    删除岗位
    """
    post_obj = post_crud.get_by_id(db, post_id=post_id)
    if not post_obj:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 检查岗位是否已分配
    if post_crud.has_users(db, post_id=post_id):
        raise HTTPException(status_code=400, detail="岗位已分配，不能删除")
    
    post_crud.remove(db, post_id=post_id)
    return ResponseModel(msg="删除成功")


@router.get("/select/options", response_model=ResponseModel[List[PostOut]], summary="获取岗位选项", description="获取岗位选项列表")
def get_post_options(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取岗位选项列表
    """
    posts = post_crud.get_enabled_posts(db)
    return ResponseModel[List[PostOut]](data=posts) 