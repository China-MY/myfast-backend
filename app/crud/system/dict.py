from typing import Dict, List, Optional, Union, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.crud.utils.base import CRUDBase
from app.models.system.dict import SysDictType, SysDictData
from app.schemas.system.dict import DictTypeCreate, DictTypeUpdate, DictDataCreate, DictDataUpdate


class CRUDDictType(CRUDBase[SysDictType, DictTypeCreate, DictTypeUpdate]):
    """字典类型数据访问层"""
    
    def get_by_id(self, db: Session, *, dict_id: int) -> Optional[SysDictType]:
        """通过字典ID获取字典类型"""
        return db.query(self.model).filter(self.model.dict_id == dict_id).first()
    
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
    
    def get_enabled_dict_types(self, db: Session) -> List[SysDictType]:
        """
        获取启用状态的字典类型列表
        """
        return db.query(self.model).filter(
            self.model.status == "0"
        ).order_by(self.model.dict_id).all()
    
    def is_duplicate(self, db: Session, *, dict_id: Optional[int] = None, dict_type: Optional[str] = None) -> bool:
        """
        检查字典类型是否重复
        """
        # 构建基础查询
        query = db.query(func.count(self.model.dict_id))

        # 如果提供了dict_type，则添加过滤条件
        if dict_type:
            query = query.filter(self.model.dict_type == dict_type)
        
        # 如果提供了dict_id，则排除这个ID的记录
        if dict_id:
            query = query.filter(self.model.dict_id != dict_id)
        
        # 执行查询并获取结果
        count = query.scalar()
        
        return count > 0
        
    def create_with_creator(self, db: Session, *, obj_in: DictTypeCreate, creator_id: int) -> SysDictType:
        """创建字典类型并记录创建者"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, create_by=str(creator_id))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_updater(self, db: Session, *, db_obj: SysDictType, obj_in: Union[DictTypeUpdate, Dict[str, Any]], updater_id: int) -> SysDictType:
        """更新字典类型并记录更新者"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["update_by"] = str(updater_id)
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, dict_id: int) -> SysDictType:
        """删除字典类型"""
        obj = db.query(self.model).filter(self.model.dict_id == dict_id).first()
        db.delete(obj)
        db.commit()
        return obj
        
    def get_with_dict_data_count(self, db: Session, *, skip: int = 0, limit: int = 100, 
                               dict_name: Optional[str] = None, dict_type: Optional[str] = None, 
                               status: Optional[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取字典类型列表并包含每个类型的字典数据数量
        """
        # 首先获取字典类型列表
        dict_types, total = self.get_multi_with_filter(
            db=db, skip=skip, limit=limit, dict_name=dict_name, dict_type=dict_type, status=status
        )
        
        # 转换为可序列化的字典并添加数据计数
        result = []
        for dict_type in dict_types:
            dict_type_dict = {
                "dict_id": dict_type.dict_id,
                "dict_name": dict_type.dict_name,
                "dict_type": dict_type.dict_type,
                "status": dict_type.status,
                "create_by": dict_type.create_by,
                "create_time": dict_type.create_time,
                "update_by": dict_type.update_by,
                "update_time": dict_type.update_time,
                "remark": dict_type.remark,
                # 获取关联的字典数据数量
                "dict_data_count": db.query(SysDictData).filter(
                    SysDictData.dict_type == dict_type.dict_type
                ).count()
            }
            result.append(dict_type_dict)
        
        return result, total


class CRUDDictData(CRUDBase[SysDictData, DictDataCreate, DictDataUpdate]):
    """字典数据访问层"""
    
    def get_by_id(self, db: Session, *, dict_code: int) -> Optional[SysDictData]:
        """通过字典编码获取字典数据"""
        return db.query(self.model).filter(self.model.dict_code == dict_code).first()
    
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
        dict_data = query.order_by(self.model.dict_code.desc()).offset(skip).limit(limit).all()
        
        return dict_data, total
    
    def is_duplicate(self, db: Session, *, dict_code: Optional[int] = None, dict_type: Optional[str] = None, dict_value: Optional[str] = None) -> bool:
        """
        检查字典数据是否重复
        - 同一个字典类型下，字典值必须唯一
        """
        # 构建基础查询
        query = db.query(func.count(self.model.dict_code))

        # 添加过滤条件
        filters = []
        
        if dict_type and dict_value:
            # 在同一字典类型下，确保值唯一
            filters.append(and_(self.model.dict_type == dict_type, self.model.dict_value == dict_value))
        
        # 如果提供了dict_code，则排除这个ID的记录
        if dict_code:
            query = query.filter(self.model.dict_code != dict_code)
        
        # 添加OR条件
        if filters:
            query = query.filter(or_(*filters))
        
        # 执行查询并获取结果
        count = query.scalar()
        
        return count > 0
        
    def create_with_creator(self, db: Session, *, obj_in: DictDataCreate, creator_id: int) -> SysDictData:
        """创建字典数据并记录创建者"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, create_by=str(creator_id))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_updater(self, db: Session, *, db_obj: SysDictData, obj_in: Union[DictDataUpdate, Dict[str, Any]], updater_id: int) -> SysDictData:
        """更新字典数据并记录更新者"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["update_by"] = str(updater_id)
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, dict_code: int) -> SysDictData:
        """删除字典数据"""
        obj = db.query(self.model).filter(self.model.dict_code == dict_code).first()
        db.delete(obj)
        db.commit()
        return obj
        
    def get_options_by_dict_type(self, db: Session, *, dict_type: str) -> List[Dict[str, Any]]:
        """
        获取指定字典类型的选项列表(用于下拉选择)
        """
        dict_data_list = self.get_by_dict_type(db=db, dict_type=dict_type)
        
        # 转换为选项格式
        options = [
            {
                "value": item.dict_value,
                "label": item.dict_label,
                "class": item.list_class,
                "is_default": item.is_default
            }
            for item in dict_data_list
        ]
        
        return options


# 实例化
dict_type = CRUDDictType(SysDictType)
dict_data = CRUDDictData(SysDictData) 