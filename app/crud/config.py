from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.config import SysConfig
from app.schemas.config import ConfigCreate, ConfigUpdate


class CRUDConfig(CRUDBase[SysConfig, ConfigCreate, ConfigUpdate]):
    """系统配置CRUD"""

    def get_by_key(self, db: Session, *, config_key: str) -> Optional[SysConfig]:
        """通过键名获取配置"""
        return db.query(self.model).filter(self.model.config_key == config_key).first()
    
    def get_by_keys(self, db: Session, *, config_keys: List[str]) -> List[SysConfig]:
        """通过多个键名获取配置列表"""
        return db.query(self.model).filter(self.model.config_key.in_(config_keys)).all()
    
    def search_by_keyword(
        self, 
        db: Session, 
        *, 
        keyword: str = None,
        config_name: str = None, 
        config_key: str = None, 
        config_type: str = None,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """搜索配置"""
        query = db.query(self.model)
        
        # 搜索条件
        if keyword:
            query = query.filter(
                (self.model.config_name.like(f"%{keyword}%")) | 
                (self.model.config_key.like(f"%{keyword}%")) |
                (self.model.config_value.like(f"%{keyword}%"))
            )
        
        if config_name:
            query = query.filter(self.model.config_name.like(f"%{config_name}%"))
        
        if config_key:
            query = query.filter(self.model.config_key.like(f"%{config_key}%"))
            
        if config_type:
            query = query.filter(self.model.config_type == config_type)
            
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(self.model.config_id).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items
        }


config = CRUDConfig(SysConfig) 