from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.post import SysPost
from app.domain.schemas.system.post import PostCreate, PostUpdate, PostInfo, PostQuery
from app.common.exception import NotFound


def get_post(db: Session, post_id: int) -> Optional[SysPost]:
    """
    根据岗位ID获取岗位信息
    """
    return db.query(SysPost).filter(
        SysPost.post_id == post_id,
        SysPost.del_flag == "0"
    ).first()


def get_post_by_code(db: Session, post_code: str) -> Optional[SysPost]:
    """
    根据岗位编码获取岗位信息
    """
    return db.query(SysPost).filter(
        SysPost.post_code == post_code,
        SysPost.del_flag == "0"
    ).first()


def get_post_by_name(db: Session, post_name: str) -> Optional[SysPost]:
    """
    根据岗位名称获取岗位信息
    """
    return db.query(SysPost).filter(
        SysPost.post_name == post_name,
        SysPost.del_flag == "0"
    ).first()


def get_posts(
    db: Session, 
    params: PostQuery
) -> Tuple[List[SysPost], int]:
    """
    获取岗位列表（分页查询）
    """
    query = db.query(SysPost).filter(SysPost.del_flag == "0")
    
    # 构建查询条件
    if params.post_code:
        query = query.filter(SysPost.post_code.like(f"%{params.post_code}%"))
    if params.post_name:
        query = query.filter(SysPost.post_name.like(f"%{params.post_name}%"))
    if params.status:
        query = query.filter(SysPost.status == params.status)
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    posts = query.order_by(SysPost.post_sort.asc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return posts, total


def create_post(
    db: Session, 
    post_data: PostCreate
) -> SysPost:
    """
    创建岗位
    """
    # 检查岗位名称是否已存在
    if get_post_by_name(db, post_data.post_name):
        raise ValueError(f"岗位名称 {post_data.post_name} 已存在")
    
    # 检查岗位编码是否已存在
    if get_post_by_code(db, post_data.post_code):
        raise ValueError(f"岗位编码 {post_data.post_code} 已存在")
    
    # 创建岗位对象
    db_post = SysPost(
        post_code=post_data.post_code,
        post_name=post_data.post_name,
        post_sort=post_data.post_sort,
        status=post_data.status,
        remark=post_data.remark
    )
    
    # 保存岗位信息
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post


def update_post(
    db: Session, 
    post_id: int, 
    post_data: PostUpdate
) -> Optional[SysPost]:
    """
    更新岗位信息
    """
    # 获取岗位信息
    db_post = get_post(db, post_id)
    if not db_post:
        raise NotFound(f"岗位ID {post_id} 不存在")
    
    # 检查岗位名称是否已存在（如果修改了岗位名称）
    if db_post.post_name != post_data.post_name and get_post_by_name(db, post_data.post_name):
        raise ValueError(f"岗位名称 {post_data.post_name} 已存在")
    
    # 检查岗位编码是否已存在（如果修改了岗位编码）
    if db_post.post_code != post_data.post_code and get_post_by_code(db, post_data.post_code):
        raise ValueError(f"岗位编码 {post_data.post_code} 已存在")
    
    # 更新岗位基本信息
    for key, value in post_data.dict().items():
        if value is not None:
            setattr(db_post, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_post)
    
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    """
    删除岗位（逻辑删除）
    """
    # 获取岗位信息
    db_post = get_post(db, post_id)
    if not db_post:
        raise NotFound(f"岗位ID {post_id} 不存在")
    
    # 检查岗位是否被用户使用
    # 这里需要判断是否有用户关联了此岗位
    if db.query(func.count()).select_from(db.query('sys_user_post').filter_by(post_id=post_id).subquery()).scalar() > 0:
        raise ValueError(f"岗位已分配，不能删除")
    
    # 逻辑删除
    db_post.del_flag = "2"
    db.commit()
    
    return True 