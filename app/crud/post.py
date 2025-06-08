from typing import Dict, List, Optional, Union, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.crud.base import CRUDBase
from app.models.post import SysPost
from app.schemas.post import PostCreate, PostUpdate


class CRUDPost(CRUDBase[SysPost, PostCreate, PostUpdate]):
    """岗位数据访问层"""
    
    def get_by_name(self, db: Session, *, post_name: str) -> Optional[SysPost]:
        """
        通过岗位名称获取岗位
        """
        return db.query(self.model).filter(self.model.post_name == post_name).first()
    
    def get_by_code(self, db: Session, *, post_code: str) -> Optional[SysPost]:
        """
        通过岗位编码获取岗位
        """
        return db.query(self.model).filter(self.model.post_code == post_code).first()
    
    def get_multi_with_filter(
        self, db: Session, *, skip: int = 0, limit: int = 100, 
        post_name: Optional[str] = None, post_code: Optional[str] = None, status: Optional[str] = None
    ) -> Tuple[List[SysPost], int]:
        """
        获取岗位列表（带过滤条件）
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if post_name:
            query = query.filter(self.model.post_name.like(f"%{post_name}%"))
        if post_code:
            query = query.filter(self.model.post_code.like(f"%{post_code}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 计算总数
        total = query.count()
        
        # 应用分页并返回数据
        posts = query.order_by(self.model.post_sort).offset(skip).limit(limit).all()
        
        return posts, total
    
    def get_enabled_posts(self, db: Session) -> List[SysPost]:
        """
        获取启用状态的岗位列表
        """
        return db.query(self.model).filter(self.model.status == "0").order_by(self.model.post_sort).all()
    
    def create(self, db: Session, *, obj_in: PostCreate, creator_id: int) -> SysPost:
        """
        创建岗位
        """
        db_obj = self.model(
            post_name=obj_in.post_name,
            post_code=obj_in.post_code,
            post_sort=obj_in.post_sort,
            status=obj_in.status,
            remark=obj_in.remark,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysPost, obj_in: Union[PostUpdate, Dict[str, Any]], updater_id: int
    ) -> SysPost:
        """
        更新岗位
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)


# 实例化
post = CRUDPost(SysPost) 