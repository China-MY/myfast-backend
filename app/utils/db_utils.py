from typing import Dict, List, Any, Optional
import re
from sqlalchemy.engine import Inspector


def camel_case(s: str) -> str:
    """
    将字符串转换为驼峰命名法
    示例：
      user_name -> userName
      USER_NAME -> userName
      UserName -> userName
    """
    # 先全部小写，再以下划线分割，最后首字母大写拼接
    s = s.lower()
    parts = s.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def get_table_info(inspector: Inspector, table_name: str) -> Optional[Dict[str, Any]]:
    """
    获取数据库表信息
    """
    try:
        # 获取表注释
        if hasattr(inspector, 'get_table_comment'):
            comment_dict = inspector.get_table_comment(table_name)
            table_comment = comment_dict.get('text', '') if comment_dict else ''
        else:
            table_comment = ''
        
        return {
            "name": table_name,
            "comment": table_comment
        }
    except Exception as e:
        print(f"获取表 {table_name} 信息失败: {str(e)}")
        return None


def get_db_tables(inspector: Inspector, exclude_tables: List[str] = None) -> List[Dict[str, str]]:
    """
    获取数据库中所有表（排除系统表和已排除的表）
    """
    if exclude_tables is None:
        exclude_tables = []
    
    # 默认排除的系统表
    default_exclude = [
        'alembic_version',   # Alembic迁移表
        'spatial_ref_sys',   # PostGIS表
        'gen_table',         # 代码生成业务表
        'gen_table_column'   # 代码生成业务表字段
    ]
    
    exclude_tables.extend(default_exclude)
    
    # 获取所有表名
    table_names = inspector.get_table_names()
    
    # 过滤排除的表
    filtered_tables = [
        table for table in table_names
        if table not in exclude_tables
    ]
    
    # 获取表信息
    result = []
    for table_name in filtered_tables:
        table_info = get_table_info(inspector, table_name)
        if table_info:
            result.append({
                "table_name": table_info["name"],
                "table_comment": table_info["comment"]
            })
    
    return result


def get_template_context(table: Dict[str, Any], columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    获取模板上下文
    """
    # 查询字段
    query_columns = [col for col in columns if col.get("is_query") == "1"]
    # 主键字段
    pk_columns = [col for col in columns if col.get("is_pk") == "1"]
    # 非主键字段
    not_pk_columns = [col for col in columns if col.get("is_pk") != "1"]
    # 所有字段
    all_columns = columns
    
    return {
        "table": table,
        "query_columns": query_columns,
        "pk_columns": pk_columns,
        "not_pk_columns": not_pk_columns,
        "columns": all_columns
    } 