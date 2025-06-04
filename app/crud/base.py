from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete, update, func, inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础CRUD操作类，提供通用的数据库操作方法
    """
    def __init__(self, model: Type[ModelType]):
        """
        初始化
        :param model: 数据模型类
        """
        self.model = model
        # 获取模型的主键列名
        self.primary_key = inspect(model).primary_key[0].name

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        根据ID获取记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 记录对象
        """
        return db.query(self.model).filter(getattr(self.model, self.primary_key) == id).first()

    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        """
        根据字段获取记录
        :param db: 数据库会话
        :param field: 字段名
        :param value: 字段值
        :return: 记录对象
        """
        return db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        获取多条记录
        :param db: 数据库会话
        :param skip: 跳过记录数
        :param limit: 返回记录数
        :return: 记录列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()
        
    def get_count(self, db: Session) -> int:
        """
        获取记录总数
        :param db: 数据库会话
        :return: 记录总数
        """
        return db.query(func.count(getattr(self.model, self.primary_key))).scalar()
            
    def get_paged(
        self, db: Session, *, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页获取记录
        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页大小
        :return: 分页记录
        """
        skip = (page - 1) * page_size
        count = self.get_count(db)
        data = self.get_multi(db=db, skip=skip, limit=page_size)
        return {
            "total": count,
            "items": data,
            "page": page,
            "pageSize": page_size
        }

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建记录
        :param db: 数据库会话
        :param obj_in: 创建模型
        :return: 创建的记录
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
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
        更新记录
        :param db: 数据库会话
        :param db_obj: 数据库记录
        :param obj_in: 更新数据
        :return: 更新的记录
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        删除记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 删除的记录
        """
        obj = db.query(self.model).get(id) or db.query(self.model).filter(
            getattr(self.model, self.primary_key) == id).first()
        db.delete(obj)
        db.commit()
        return obj 