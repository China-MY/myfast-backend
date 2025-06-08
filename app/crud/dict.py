from typing import Dict, List, Optional, Union, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.crud.base import CRUDBase
from app.models.dict import SysDictType, SysDictData
from app.schemas.dict import DictTypeCreate, DictTypeUpdate, DictDataCreate, DictDataUpdate


class CRUDDictType(CRUDBase[SysDictType, DictTypeCreate, DictTypeUpdate]):
    """字典类型数据访问层"""
    
    def get_by_name(self, db: Session, *, dict_name: str) -> Optional[SysDictType]:
        """
        通过字典名称获取字典类型
        """
        return db.query(self.model).filter(self.model.dict_name == dict_name).first()
    
    def get_by_type(self, db: Session, *, dict_type: str) -> Optional[SysDictType]:
        """
        通过字典类型获取字典类型
        """
        return db.query(self.model).filter(self.model.dict_type == dict_type).first()
    
    def get_multi_with_filter(
        self, db: Session, *, skip: int = 0, limit: int = 100, 
        dict_name: Optional[str] = None, dict_type: Optional[str] = None, status: Optional[str] = None
    ) -> Tuple[List[SysDictType], int]:
        """
        获取字典类型列表（带过滤条件）
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if dict_name:
            query = query.filter(self.model.dict_name.like(f"%{dict_name}%"))
        if dict_type:
            query = query.filter(self.model.dict_type.like(f"%{dict_type}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 计算总数
        total = query.count()
        
        # 应用分页并返回数据
        dict_types = query.order_by(self.model.dict_id.desc()).offset(skip).limit(limit).all()
        
        return dict_types, total
    
    def create(self, db: Session, *, obj_in: DictTypeCreate, creator_id: int) -> SysDictType:
        """
        创建字典类型
        """
        db_obj = self.model(
            dict_name=obj_in.dict_name,
            dict_type=obj_in.dict_type,
            status=obj_in.status,
            remark=obj_in.remark,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysDictType, obj_in: Union[DictTypeUpdate, Dict[str, Any]], updater_id: int
    ) -> SysDictType:
        """
        更新字典类型
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)


class CRUDDictData(CRUDBase[SysDictData, DictDataCreate, DictDataUpdate]):
    """字典数据访问层"""
    
    def get_by_dict_type(self, db: Session, *, dict_type: str) -> List[SysDictData]:
        """
        通过字典类型获取字典数据
        """
        return (
            db.query(self.model)
            .filter(self.model.dict_type == dict_type, self.model.status == "0")
            .order_by(self.model.dict_sort)
            .all()
        )
    
    def get_multi_with_filter(
        self, db: Session, *, skip: int = 0, limit: int = 100, 
        dict_type: Optional[str] = None, dict_label: Optional[str] = None, status: Optional[str] = None
    ) -> Tuple[List[SysDictData], int]:
        """
        获取字典数据列表（带过滤条件）
        """
        query = db.query(self.model)
        
        # 应用过滤条件
        if dict_type:
            query = query.filter(self.model.dict_type == dict_type)
        if dict_label:
            query = query.filter(self.model.dict_label.like(f"%{dict_label}%"))
        if status:
            query = query.filter(self.model.status == status)
        
        # 计算总数
        total = query.count()
        
        # 应用分页并返回数据
        dict_data = query.order_by(self.model.dict_sort).offset(skip).limit(limit).all()
        
        return dict_data, total
    
    def create(self, db: Session, *, obj_in: DictDataCreate, creator_id: int) -> SysDictData:
        """
        创建字典数据
        """
        db_obj = self.model(
            dict_sort=obj_in.dict_sort,
            dict_label=obj_in.dict_label,
            dict_value=obj_in.dict_value,
            dict_type=obj_in.dict_type,
            css_class=obj_in.css_class,
            list_class=obj_in.list_class,
            is_default=obj_in.is_default,
            status=obj_in.status,
            remark=obj_in.remark,
            create_by=str(creator_id)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: SysDictData, obj_in: Union[DictDataUpdate, Dict[str, Any]], updater_id: int
    ) -> SysDictData:
        """
        更新字典数据
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 手动设置更新人
        update_data["update_by"] = str(updater_id)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)


# 实例化
dict_type = CRUDDictType(SysDictType)
dict_data = CRUDDictData(SysDictData) 