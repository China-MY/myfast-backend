from typing import Any, Dict, List, Optional, Union, Tuple
from sqlalchemy.orm import Session

from app.crud.utils.base import CRUDBase
from app.models.utils.config import SysConfig
from app.schemas.utils.config import ConfigCreate, ConfigUpdate


class CRUDConfig(CRUDBase[SysConfig, ConfigCreate, ConfigUpdate]):
    """系统配置CRUD"""

    def create(self, db: Session, *, obj_in: ConfigCreate, creator_id: int = None) -> SysConfig:
        """创建参数配置"""
        db_obj = SysConfig(
            config_name=obj_in.config_name,
            config_key=obj_in.config_key,
            config_value=obj_in.config_value,
            config_type=obj_in.config_type,
            remark=obj_in.remark,
            create_by=str(creator_id) if creator_id else ""
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: SysConfig, obj_in: Union[ConfigUpdate, Dict[str, Any]], updater_id: int = None) -> SysConfig:
        """更新参数配置"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 设置更新人
        if updater_id:
            update_data["update_by"] = str(updater_id)
            
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, config_id: int) -> None:
        """删除参数配置"""
        db_obj = db.query(self.model).filter(self.model.config_id == config_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            
    def get_by_id(self, db: Session, *, config_id: int) -> Optional[SysConfig]:
        """通过ID获取配置"""
        return db.query(self.model).filter(self.model.config_id == config_id).first()

    def get_by_key(self, db: Session, *, config_key: str) -> Optional[SysConfig]:
        """通过键名获取配置"""
        return db.query(self.model).filter(self.model.config_key == config_key).first()
    
    def get_by_keys(self, db: Session, *, config_keys: List[str]) -> List[SysConfig]:
        """通过多个键名获取配置列表"""
        return db.query(self.model).filter(self.model.config_key.in_(config_keys)).all()
    
    def get_config_value_by_key(self, db: Session, *, config_key: str) -> Optional[str]:
        """通过键名获取配置值"""
        config = self.get_by_key(db, config_key=config_key)
        return config.config_value if config else None
    
    def get_multi_with_filter(
        self, 
        db: Session, 
        *, 
        skip: int = 0,
        limit: int = 100,
        config_name: str = None, 
        config_key: str = None, 
        config_type: str = None,
    ) -> Tuple[List[SysConfig], int]:
        """获取参数列表，带过滤条件"""
        query = db.query(self.model)
        
        # 应用过滤条件
        if config_name:
            query = query.filter(self.model.config_name.like(f"%{config_name}%"))
        
        if config_key:
            query = query.filter(self.model.config_key.like(f"%{config_key}%"))
            
        if config_type:
            query = query.filter(self.model.config_type == config_type)
        
        # 计算总数
        total = query.count()
        
        # 应用分页并返回结果
        configs = query.order_by(self.model.config_id).offset(skip).limit(limit).all()
        
        return configs, total
    
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