from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import Base

# 定义模型类型变量
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用CRUD操作基类
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        通过ID获取对象
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        """
        获取多个对象
        """
        query = db.query(self.model)
        # 应用过滤条件
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, str) and field not in ["del_flag", "status"]:
                    query = query.filter(getattr(self.model, field).like(f"%{value}%"))
                else:
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session, **filters) -> int:
        """
        获取符合条件的对象数量
        """
        query = db.query(func.count(self.model.id))
        # 应用过滤条件
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, str) and field not in ["del_flag", "status"]:
                    query = query.filter(getattr(self.model, field).like(f"%{value}%"))
                else:
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.scalar()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建对象
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新对象
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        删除对象
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
        
    def remove_multi(self, db: Session, *, ids: List[int]) -> List[ModelType]:
        """
        批量删除对象
        """
        objs = db.query(self.model).filter(self.model.id.in_(ids)).all()
        for obj in objs:
            db.delete(obj)
        db.commit()
        return objs 