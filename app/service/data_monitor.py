from typing import Dict, List, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session


class DataMonitorService:
    """
    数据库监控服务
    """
    
    def get_db_info(self, db: Session) -> Dict[str, Any]:
        """
        获取数据库基本信息
        """
        # 获取数据库类型和版本
        db_type = db.bind.dialect.name
        
        if db_type == "mysql":
            return self._get_mysql_info(db)
        elif db_type == "postgresql":
            return self._get_postgresql_info(db)
        elif db_type == "sqlite":
            return self._get_sqlite_info(db)
        else:
            return {
                "db_type": db_type,
                "version": "未知",
                "tables_count": len(self.get_table_info(db)),
                "size": "未知"
            }
    
    def _get_mysql_info(self, db: Session) -> Dict[str, Any]:
        """
        获取MySQL数据库信息
        """
        # 获取版本
        version_query = text("SELECT VERSION() as version")
        version_result = db.execute(version_query).first()
        version = version_result.version if version_result else "未知"
        
        # 获取数据库名称
        db_name_query = text("SELECT DATABASE() as db_name")
        db_name_result = db.execute(db_name_query).first()
        db_name = db_name_result.db_name if db_name_result else "未知"
        
        # 获取数据库大小
        size_query = text("""
            SELECT 
                SUM(data_length + index_length) / 1024 / 1024 as size_mb
            FROM 
                information_schema.tables
            WHERE 
                table_schema = :db_name
        """)
        size_result = db.execute(size_query, {"db_name": db_name}).first()
        size = f"{size_result.size_mb:.2f} MB" if size_result and size_result.size_mb else "未知"
        
        # 获取表数量
        tables_count = len(self.get_table_info(db))
        
        # 获取连接信息
        conn_query = text("""
            SELECT 
                COUNT(*) as connections
            FROM 
                information_schema.processlist
        """)
        conn_result = db.execute(conn_query).first()
        connections = conn_result.connections if conn_result else 0
        
        return {
            "db_type": "MySQL",
            "version": version,
            "db_name": db_name,
            "size": size,
            "tables_count": tables_count,
            "connections": connections
        }
    
    def _get_postgresql_info(self, db: Session) -> Dict[str, Any]:
        """
        获取PostgreSQL数据库信息
        """
        # 获取版本
        version_query = text("SELECT version()")
        version_result = db.execute(version_query).first()
        version = version_result[0] if version_result else "未知"
        
        # 获取数据库名称
        db_name_query = text("SELECT current_database()")
        db_name_result = db.execute(db_name_query).first()
        db_name = db_name_result[0] if db_name_result else "未知"
        
        # 获取数据库大小
        size_query = text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """)
        size_result = db.execute(size_query).first()
        size = size_result.size if size_result else "未知"
        
        # 获取表数量
        tables_count = len(self.get_table_info(db))
        
        # 获取连接信息
        conn_query = text("""
            SELECT COUNT(*) as connections FROM pg_stat_activity
        """)
        conn_result = db.execute(conn_query).first()
        connections = conn_result.connections if conn_result else 0
        
        return {
            "db_type": "PostgreSQL",
            "version": version,
            "db_name": db_name,
            "size": size,
            "tables_count": tables_count,
            "connections": connections
        }
    
    def _get_sqlite_info(self, db: Session) -> Dict[str, Any]:
        """
        获取SQLite数据库信息
        """
        # 获取版本
        version_query = text("SELECT sqlite_version() as version")
        version_result = db.execute(version_query).first()
        version = version_result.version if version_result else "未知"
        
        # 获取表数量
        tables_count = len(self.get_table_info(db))
        
        return {
            "db_type": "SQLite",
            "version": version,
            "db_name": "SQLite数据库",
            "size": "未知",
            "tables_count": tables_count,
            "connections": 1
        }
    
    def get_table_info(self, db: Session) -> List[Dict[str, Any]]:
        """
        获取数据库所有表信息
        """
        inspector = inspect(db.bind)
        tables = []
        
        for table_name in inspector.get_table_names():
            # 获取表的列信息
            columns = inspector.get_columns(table_name)
            
            # 获取表的行数
            row_count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
            try:
                row_count_result = db.execute(row_count_query).first()
                row_count = row_count_result.count if row_count_result else 0
            except:
                row_count = 0
            
            tables.append({
                "table_name": table_name,
                "columns_count": len(columns),
                "row_count": row_count
            })
        
        return tables
    
    def get_table_detail(self, db: Session, table_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定表的详细信息
        """
        inspector = inspect(db.bind)
        
        # 检查表是否存在
        if table_name not in inspector.get_table_names():
            return None
        
        # 获取表的列信息
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": str(column["default"]) if column["default"] is not None else None,
                "primary_key": column.get("primary_key", False)
            })
        
        # 获取表的主键
        primary_keys = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        
        # 获取表的外键
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "name": fk.get("name"),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns"),
                "constrained_columns": fk.get("constrained_columns")
            })
        
        # 获取表的索引
        indexes = []
        for idx in inspector.get_indexes(table_name):
            indexes.append({
                "name": idx.get("name"),
                "unique": idx.get("unique", False),
                "columns": idx.get("column_names", [])
            })
        
        # 获取表的行数
        row_count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
        try:
            row_count_result = db.execute(row_count_query).first()
            row_count = row_count_result.count if row_count_result else 0
        except:
            row_count = 0
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "indexes": indexes,
            "row_count": row_count
        }


# 实例化服务
data_monitor_service = DataMonitorService() 