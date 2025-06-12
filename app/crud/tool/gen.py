from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, inspect
from fastapi.encoders import jsonable_encoder

from app.db.session import engine
from app.models.tool.gen import GenTable, GenTableColumn
from app.schemas.tool.gen import GenTableCreate, GenTableUpdate, GenTableColumnCreate, GenTableColumnUpdate, TableQueryParams
from app.utils.db_utils import camel_case, get_table_info


class CRUDGenTable:
    """代码生成表CRUD操作类"""
    
    def get(self, db: Session, id: int) -> Optional[GenTable]:
        """获取单个表信息"""
        return db.query(GenTable).filter(GenTable.id == id).first()
    
    def get_by_name(self, db: Session, table_name: str) -> Optional[GenTable]:
        """根据表名获取表信息"""
        return db.query(GenTable).filter(GenTable.table_name == table_name).first()
    
    def get_list(self, db: Session, *, query: TableQueryParams) -> List[GenTable]:
        """获取表列表"""
        filters = []
        if query.table_name:
            filters.append(GenTable.table_name.like(f"%{query.table_name}%"))
        if query.table_comment:
            filters.append(GenTable.table_comment.like(f"%{query.table_comment}%"))
        if query.begin_time and query.end_time:
            filters.append(GenTable.create_time.between(query.begin_time, query.end_time))
        
        if filters:
            return db.query(GenTable).filter(and_(*filters)).order_by(desc(GenTable.create_time)).offset((query.page_num - 1) * query.page_size).limit(query.page_size).all()
        else:
            return db.query(GenTable).order_by(desc(GenTable.create_time)).offset((query.page_num - 1) * query.page_size).limit(query.page_size).all()
    
    def get_count(self, db: Session, *, query: TableQueryParams) -> int:
        """获取表总数"""
        filters = []
        if query.table_name:
            filters.append(GenTable.table_name.like(f"%{query.table_name}%"))
        if query.table_comment:
            filters.append(GenTable.table_comment.like(f"%{query.table_comment}%"))
        if query.begin_time and query.end_time:
            filters.append(GenTable.create_time.between(query.begin_time, query.end_time))
        
        if filters:
            return db.query(func.count(GenTable.id)).filter(and_(*filters)).scalar()
        else:
            return db.query(func.count(GenTable.id)).scalar()
    
    def create(self, db: Session, *, obj_in: GenTableCreate) -> GenTable:
        """创建表信息"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = GenTable(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: GenTable, obj_in: Union[GenTableUpdate, Dict[str, Any]]) -> GenTable:
        """更新表信息"""
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
    
    def remove(self, db: Session, *, id: int) -> GenTable:
        """删除表信息"""
        obj = db.query(GenTable).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    def remove_batch(self, db: Session, *, ids: List[int]) -> List[GenTable]:
        """批量删除表信息"""
        objs = []
        for id in ids:
            obj = db.query(GenTable).get(id)
            if obj:
                db.delete(obj)
                objs.append(obj)
        db.commit()
        return objs
    
    def import_tables(self, db: Session, *, tables: List[str]) -> List[GenTable]:
        """导入数据库表"""
        inspector = inspect(engine)
        imported_tables = []
        
        for table_name in tables:
            # 检查表是否已导入
            existing_table = self.get_by_name(db, table_name)
            if existing_table:
                continue
            
            # 获取表信息
            table_info = get_table_info(inspector, table_name)
            if not table_info:
                continue
            
            # 表名转换为类名（驼峰命名）
            class_name = camel_case(table_name.replace("_", " ")).replace(" ", "")
            # 模块名（取表名第一部分）
            module_name = table_name.split("_")[0] if "_" in table_name else table_name
            # 业务名（取表名第二部分，如果没有则使用表名）
            business_name = table_name.split("_")[1] if "_" in table_name and len(table_name.split("_")) > 1 else table_name
            
            # 创建表对象
            table_obj = GenTable(
                table_name=table_name,
                table_comment=table_info.get("comment", ""),
                class_name=class_name,
                package_name="app.models",
                module_name=module_name,
                business_name=business_name,
                function_name=table_info.get("comment", "").split("表")[0] if "表" in table_info.get("comment", "") else business_name,
                tpl_category="crud",
                function_author="admin"
            )
            db.add(table_obj)
            db.flush()  # 获取表ID
            
            # 获取表的所有列
            columns = inspector.get_columns(table_name)
            # 获取主键列
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint.get("constrained_columns", []) if pk_constraint else []
            
            for index, column in enumerate(columns):
                column_name = column["name"]
                is_pk = "1" if column_name in pk_columns else "0"
                is_increment = "1" if column.get("autoincrement", False) else "0"
                
                # 判断字段类型
                db_column_type = str(column["type"])
                python_type = self._map_db_type_to_python(db_column_type)
                
                # 驼峰命名
                field_name = camel_case(column_name.replace("_", " ")).replace(" ", "")
                # 首字母小写
                field_name = field_name[0].lower() + field_name[1:] if field_name else ""
                
                column_obj = GenTableColumn(
                    table_id=table_obj.id,
                    column_name=column_name,
                    column_comment=column.get("comment", ""),
                    column_type=db_column_type,
                    python_type=python_type,
                    field_name=field_name,
                    is_pk=is_pk,
                    is_increment=is_increment,
                    is_required="1" if not column.get("nullable", True) else "0",
                    is_insert="1",
                    is_edit="1" if is_pk != "1" else "0",
                    is_list="1",
                    is_query="1" if field_name in ["name", "title", "type", "status"] else "0",
                    query_type="EQ",
                    html_type=self._get_html_type(db_column_type, field_name),
                    sort=index
                )
                db.add(column_obj)
            
            imported_tables.append(table_obj)
        
        db.commit()
        return imported_tables
    
    def _map_db_type_to_python(self, db_type: str) -> str:
        """将数据库类型映射为Python类型"""
        db_type = db_type.lower()
        if any(x in db_type for x in ['int', 'number', 'numeric']):
            return 'int'
        elif any(x in db_type for x in ['float', 'double', 'decimal']):
            return 'float'
        elif any(x in db_type for x in ['bool']):
            return 'bool'
        elif any(x in db_type for x in ['datetime', 'timestamp']):
            return 'datetime'
        elif any(x in db_type for x in ['date']):
            return 'date'
        elif any(x in db_type for x in ['time']):
            return 'time'
        elif any(x in db_type for x in ['json']):
            return 'dict'
        else:
            return 'str'
    
    def _get_html_type(self, db_type: str, field_name: str) -> str:
        """获取HTML展示类型"""
        if any(x in field_name.lower() for x in ['status', 'type', 'sex', 'gender']):
            return 'select'
        elif 'text' in db_type.lower():
            return 'textarea'
        elif any(x in db_type.lower() for x in ['datetime', 'timestamp']):
            return 'datetime'
        elif any(x in db_type.lower() for x in ['date']):
            return 'date'
        elif any(x in db_type.lower() for x in ['time']):
            return 'time'
        elif any(x in db_type.lower() for x in ['image', 'file']):
            return 'upload'
        else:
            return 'input'


class CRUDGenTableColumn:
    """代码生成表字段CRUD操作类"""
    
    def get(self, db: Session, id: int) -> Optional[GenTableColumn]:
        """获取单个字段信息"""
        return db.query(GenTableColumn).filter(GenTableColumn.id == id).first()
    
    def get_list_by_table_id(self, db: Session, table_id: int) -> List[GenTableColumn]:
        """获取表下所有字段"""
        return db.query(GenTableColumn).filter(GenTableColumn.table_id == table_id).order_by(GenTableColumn.sort).all()
    
    def create(self, db: Session, *, obj_in: GenTableColumnCreate) -> GenTableColumn:
        """创建字段信息"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = GenTableColumn(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: GenTableColumn, obj_in: Union[GenTableColumnUpdate, Dict[str, Any]]) -> GenTableColumn:
        """更新字段信息"""
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
    
    def remove(self, db: Session, *, id: int) -> GenTableColumn:
        """删除字段信息"""
        obj = db.query(GenTableColumn).get(id)
        db.delete(obj)
        db.commit()
        return obj


# 创建CRUD实例
gen_table = CRUDGenTable()
gen_table_column = CRUDGenTableColumn() 