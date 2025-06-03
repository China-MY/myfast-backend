from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import Base

# 定义泛型类型变量
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
QuerySchemaType = TypeVar("QuerySchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, QuerySchemaType]):
    """
    提供标准CRUD操作的通用服务基类
    """
    def __init__(self, model: Type[ModelType]):
        """
        初始化服务
        :param model: SQLAlchemy模型类
        """
        self.model = model
    
    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        根据ID获取记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 模型实例或None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_list(
        self, 
        db: Session, 
        query_params: Optional[QuerySchemaType] = None
    ) -> Tuple[List[ModelType], int]:
        """
        获取记录列表，支持分页和过滤
        :param db: 数据库会话
        :param query_params: 查询参数
        :return: (记录列表, 总数)
        """
        query = db.query(self.model)
        
        # 如果有查询参数，应用过滤条件
        if query_params:
            filters = self._get_filters(query_params)
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        # 获取总数
        total = query.count()
        
        # 分页
        if hasattr(query_params, "page_num") and hasattr(query_params, "page_size"):
            page_num = getattr(query_params, "page_num", 1)
            page_size = getattr(query_params, "page_size", 10)
            query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        # 排序
        if hasattr(query_params, "order_by") and hasattr(query_params, "is_desc"):
            order_by = getattr(query_params, "order_by")
            is_desc = getattr(query_params, "is_desc", False)
            if order_by:
                order_column = getattr(self.model, order_by, None)
                if order_column:
                    query = query.order_by(order_column.desc() if is_desc else order_column)
        
        return query.all(), total
    
    def _get_filters(self, query_params: QuerySchemaType) -> List[Any]:
        """
        根据查询参数构建过滤条件
        :param query_params: 查询参数
        :return: 过滤条件列表
        """
        filters = []
        for field, value in query_params.dict(exclude_unset=True).items():
            # 跳过分页和排序参数
            if field in ["page_num", "page_size", "order_by", "is_desc"]:
                continue
            
            # 跳过空值
            if value is None:
                continue
            
            # 获取模型字段
            model_field = getattr(self.model, field, None)
            if model_field is None:
                continue
            
            # 字符串模糊查询
            if isinstance(value, str) and value:
                filters.append(model_field.like(f"%{value}%"))
            # 其他类型精确匹配
            elif value is not None:
                filters.append(model_field == value)
        
        return filters
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        创建记录
        :param db: 数据库会话
        :param obj_in: 创建数据模型
        :return: 创建的模型实例
        """
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        :param db: 数据库会话
        :param id: 记录ID
        :param obj_in: 更新数据
        :return: 更新后的模型实例
        """
        db_obj = self.get_by_id(db, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 将更新数据转换为字典
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 更新字段
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: Any) -> bool:
        """
        删除记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 是否成功
        """
        db_obj = self.get_by_id(db, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        db.delete(db_obj)
        db.commit()
        return True 