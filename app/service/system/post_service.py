from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.system.post import SysPost
from app.common.constants import StatusEnum
from app.common.exception import BusinessException

class PostService:
    """岗位服务类"""
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> Optional[SysPost]:
        """根据岗位ID获取岗位信息"""
        return db.query(SysPost).filter(SysPost.post_id == post_id).first()
    
    @staticmethod
    def get_post_by_code(db: Session, post_code: str) -> Optional[SysPost]:
        """根据岗位编码获取岗位信息"""
        return db.query(SysPost).filter(SysPost.post_code == post_code).first()
    
    @staticmethod
    def get_posts(
        db: Session,
        page_num: int = 1, 
        page_size: int = 10,
        post_code: Optional[str] = None,
        post_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取岗位列表"""
        query = db.query(SysPost)
        
        # 应用过滤条件
        if post_code:
            query = query.filter(SysPost.post_code.like(f"%{post_code}%"))
        if post_name:
            query = query.filter(SysPost.post_name.like(f"%{post_name}%"))
        if status:
            query = query.filter(SysPost.status == status)
        
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(SysPost.post_sort).offset((page_num - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items,
            "page_num": page_num,
            "page_size": page_size
        }
    
    @staticmethod
    def create_post(
        db: Session, 
        post_data: Dict[str, Any],
        current_user_name: str
    ) -> SysPost:
        """创建岗位"""
        # 检查岗位编码是否已存在
        exist_post = PostService.get_post_by_code(db, post_data["post_code"])
        if exist_post:
            raise BusinessException(code=400, msg=f"岗位编码 {post_data['post_code']} 已存在")
        
        # 设置创建信息
        post_data["create_by"] = current_user_name
        post_data["create_time"] = datetime.now()
        
        # 创建岗位
        post = SysPost(**post_data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def update_post(
        db: Session, 
        post: SysPost,
        post_data: Dict[str, Any],
        current_user_name: str
    ) -> SysPost:
        """更新岗位"""
        # 检查岗位编码是否已存在
        if "post_code" in post_data and post_data["post_code"] != post.post_code:
            exist_post = PostService.get_post_by_code(db, post_data["post_code"])
            if exist_post:
                raise BusinessException(code=400, msg=f"岗位编码 {post_data['post_code']} 已存在")
        
        # 设置更新信息
        post_data["update_by"] = current_user_name
        post_data["update_time"] = datetime.now()
        
        # 更新岗位信息
        for key, value in post_data.items():
            if hasattr(post, key) and value is not None:
                setattr(post, key, value)
        
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def delete_post(db: Session, post_id: int) -> bool:
        """删除岗位"""
        post = PostService.get_post_by_id(db, post_id)
        if not post:
            return False
        
        # 检查岗位是否已分配用户
        if post.users and len(post.users) > 0:
            raise BusinessException(code=400, msg="岗位已分配用户，不允许删除")
        
        # 删除岗位
        db.delete(post)
        db.commit()
        return True 