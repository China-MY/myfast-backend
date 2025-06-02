from typing import List, Optional, Dict, Any, Tuple, BytesIO
import json
import os
import zipfile
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect, func, and_, or_
from sqlalchemy.sql import sqltypes
import re

from app.domain.models.tool.gen_table import GenTable, GenTableColumn
from app.domain.schemas.tool.gen_table import (
    GenTableCreate, GenTableUpdate, GenTableInfo, GenTableQuery,
    GenTableColumnCreate, GenTableColumnUpdate, GenTableColumnInfo,
    ImportTableQuery, GenPreviewItem
)
from app.common.exception import NotFound


def get_gen_table(db: Session, table_id: int) -> Optional[GenTable]:
    """
    根据表ID获取代码生成表信息
    """
    return db.query(GenTable).filter(GenTable.table_id == table_id).first()


def get_gen_table_by_name(db: Session, table_name: str) -> Optional[GenTable]:
    """
    根据表名获取代码生成表信息
    """
    return db.query(GenTable).filter(GenTable.table_name == table_name).first()


def get_gen_tables(
    db: Session, 
    params: GenTableQuery
) -> Tuple[List[GenTable], int]:
    """
    获取代码生成表列表(分页查询)
    """
    query = db.query(GenTable)
    
    # 构建查询条件
    if params.table_name:
        query = query.filter(GenTable.table_name.like(f"%{params.table_name}%"))
    if params.table_comment:
        query = query.filter(GenTable.table_comment.like(f"%{params.table_comment}%"))
    if params.begin_time and params.end_time:
        query = query.filter(
            GenTable.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    tables = query.order_by(GenTable.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return tables, total


def get_db_table_list(
    db: Session, 
    params: ImportTableQuery
) -> List[Dict[str, Any]]:
    """
    获取数据库表列表
    """
    # 获取已导入的表名
    imported_tables = db.query(GenTable.table_name).all()
    imported_table_names = [table.table_name for table in imported_tables]
    
    # 构建SQL查询，获取所有表信息
    sql = """
    SELECT 
        table_name, table_comment, create_time, update_time
    FROM 
        information_schema.tables
    WHERE 
        table_schema = (SELECT DATABASE()) 
        AND table_name NOT LIKE 'gen_%' 
        AND table_name NOT IN :imported_tables
    """
    
    # 添加过滤条件
    if params.table_name:
        sql += f" AND table_name LIKE :table_name"
    if params.table_comment:
        sql += f" AND table_comment LIKE :table_comment"
    
    # 按创建时间排序
    sql += " ORDER BY create_time DESC"
    
    # 执行查询
    query_params = {
        "imported_tables": tuple(imported_table_names) if imported_table_names else ("",),
        "table_name": f"%{params.table_name}%" if params.table_name else None,
        "table_comment": f"%{params.table_comment}%" if params.table_comment else None
    }
    
    result = db.execute(text(sql), query_params).fetchall()
    
    # 转换结果
    tables = []
    for row in result:
        tables.append({
            "table_name": row[0],
            "table_comment": row[1],
            "create_time": row[2],
            "update_time": row[3]
        })
    
    return tables


def get_db_table_columns(db: Session, table_name: str) -> List[Dict[str, Any]]:
    """
    获取数据库表字段信息
    """
    # 构建SQL查询，获取表字段信息
    sql = """
    SELECT 
        column_name, column_comment, column_type, 
        column_key, extra, is_nullable, ordinal_position
    FROM 
        information_schema.columns
    WHERE 
        table_schema = (SELECT DATABASE()) 
        AND table_name = :table_name
    ORDER BY 
        ordinal_position
    """
    
    # 执行查询
    result = db.execute(text(sql), {"table_name": table_name}).fetchall()
    
    # 转换结果
    columns = []
    for row in result:
        column_name = row[0]
        column_comment = row[1]
        column_type = row[2]
        column_key = row[3]
        extra = row[4]
        is_nullable = row[5]
        ordinal_position = row[6]
        
        # 判断是否主键
        is_pk = "1" if column_key == "PRI" else "0"
        
        # 判断是否自增
        is_increment = "1" if extra == "auto_increment" else "0"
        
        # 判断是否必填
        is_required = "1" if is_nullable == "NO" else "0"
        
        # 判断是否编辑字段
        is_edit = "1" if column_name not in ["create_time", "create_by", "update_time", "update_by"] else "0"
        
        # 判断是否列表字段
        is_list = "1" if column_name not in ["create_by", "update_by", "remark"] else "0"
        
        # 判断是否查询字段
        is_query = "1" if column_name in ["id", "name", "status", "type"] else "0"
        
        # 判断查询类型
        query_type = "EQ"
        if column_name in ["name", "title", "comment", "remark"]:
            query_type = "LIKE"
        
        # 判断HTML类型
        html_type = "input"
        if "time" in column_name.lower():
            html_type = "datetime"
        elif column_name in ["status", "type", "sex", "gender"]:
            html_type = "select"
        elif column_name in ["content", "remark"]:
            html_type = "textarea"
        
        # 获取Java字段类型
        java_type = get_java_type(column_type)
        
        # 获取Java字段名
        java_field = convert_to_java_field(column_name)
        
        columns.append({
            "column_name": column_name,
            "column_comment": column_comment,
            "column_type": column_type,
            "java_type": java_type,
            "java_field": java_field,
            "is_pk": is_pk,
            "is_increment": is_increment,
            "is_required": is_required,
            "is_insert": "1",
            "is_edit": is_edit,
            "is_list": is_list,
            "is_query": is_query,
            "query_type": query_type,
            "html_type": html_type,
            "dict_type": "",
            "sort": ordinal_position
        })
    
    return columns


def import_table(db: Session, table_name: str, user_name: str) -> GenTable:
    """
    导入表结构
    """
    # 查询表信息
    sql = """
    SELECT 
        table_name, table_comment, create_time, update_time
    FROM 
        information_schema.tables
    WHERE 
        table_schema = (SELECT DATABASE()) 
        AND table_name = :table_name
    """
    
    table_info = db.execute(text(sql), {"table_name": table_name}).fetchone()
    if not table_info:
        raise ValueError(f"表 {table_name} 不存在")
    
    # 获取表注释
    table_comment = table_info[1] or ""
    
    # 获取表字段信息
    columns = get_db_table_columns(db, table_name)
    
    # 生成表类名
    class_name = convert_to_class_name(table_name)
    
    # 生成业务名
    business_name = get_business_name(table_name)
    
    # 创建代码生成表
    gen_table = GenTable(
        table_name=table_name,
        table_comment=table_comment,
        class_name=class_name,
        tpl_category="crud",
        package_name="app",
        module_name=business_name,
        business_name=business_name,
        function_name=table_comment.split("表")[0] if "表" in table_comment else table_comment,
        function_author=user_name,
        create_by=user_name
    )
    
    db.add(gen_table)
    db.flush()
    
    # 创建代码生成表字段
    for column in columns:
        gen_column = GenTableColumn(
            table_id=gen_table.table_id,
            column_name=column["column_name"],
            column_comment=column["column_comment"],
            column_type=column["column_type"],
            java_type=column["java_type"],
            java_field=column["java_field"],
            is_pk=column["is_pk"],
            is_increment=column["is_increment"],
            is_required=column["is_required"],
            is_insert=column["is_insert"],
            is_edit=column["is_edit"],
            is_list=column["is_list"],
            is_query=column["is_query"],
            query_type=column["query_type"],
            html_type=column["html_type"],
            dict_type=column["dict_type"],
            sort=column["sort"],
            create_by=user_name
        )
        db.add(gen_column)
    
    db.commit()
    db.refresh(gen_table)
    
    return gen_table


def update_gen_table(
    db: Session, 
    table_id: int, 
    table_data: GenTableUpdate,
    user_name: str
) -> Optional[GenTable]:
    """
    更新代码生成表信息
    """
    # 获取表信息
    gen_table = get_gen_table(db, table_id)
    if not gen_table:
        raise NotFound(f"表ID {table_id} 不存在")
    
    # 更新表信息
    for key, value in table_data.dict(exclude={"table_id"}).items():
        setattr(gen_table, key, value)
    
    # 更新更新者和更新时间
    gen_table.update_by = user_name
    gen_table.update_time = datetime.now()
    
    # 提交事务
    db.commit()
    db.refresh(gen_table)
    
    return gen_table


def update_gen_column(
    db: Session, 
    column_id: int, 
    column_data: GenTableColumnUpdate,
    user_name: str
) -> Optional[GenTableColumn]:
    """
    更新代码生成表字段信息
    """
    # 获取字段信息
    gen_column = db.query(GenTableColumn).filter(
        GenTableColumn.column_id == column_id
    ).first()
    
    if not gen_column:
        raise NotFound(f"字段ID {column_id} 不存在")
    
    # 更新字段信息
    for key, value in column_data.dict(exclude={"column_id", "table_id"}).items():
        setattr(gen_column, key, value)
    
    # 更新更新者和更新时间
    gen_column.update_by = user_name
    gen_column.update_time = datetime.now()
    
    # 提交事务
    db.commit()
    db.refresh(gen_column)
    
    return gen_column


def delete_gen_table(db: Session, table_id: int) -> bool:
    """
    删除代码生成表信息
    """
    # 获取表信息
    gen_table = get_gen_table(db, table_id)
    if not gen_table:
        raise NotFound(f"表ID {table_id} 不存在")
    
    # 删除表字段
    db.query(GenTableColumn).filter(
        GenTableColumn.table_id == table_id
    ).delete()
    
    # 删除表信息
    db.delete(gen_table)
    db.commit()
    
    return True


def preview_code(db: Session, table_id: int) -> List[Dict[str, str]]:
    """
    预览代码
    """
    # 获取表信息
    gen_table = get_gen_table(db, table_id)
    if not gen_table:
        raise NotFound(f"表ID {table_id} 不存在")
    
    # 获取表字段信息
    gen_columns = db.query(GenTableColumn).filter(
        GenTableColumn.table_id == table_id
    ).order_by(GenTableColumn.sort.asc()).all()
    
    # 生成代码
    templates = get_templates(gen_table.tpl_category)
    result = []
    
    # 模板变量
    for template in templates:
        template_name = template["template_name"]
        file_name = get_file_name(template_name, gen_table)
        content = generate_code(template["template_content"], gen_table, gen_columns)
        
        result.append({
            "file_name": file_name,
            "content": content
        })
    
    return result


def download_code(db: Session, table_id: int) -> BytesIO:
    """
    下载代码
    """
    # 预览代码
    preview_list = preview_code(db, table_id)
    
    # 创建内存文件
    zip_buffer = BytesIO()
    
    # 创建ZIP文件
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 添加文件
        for item in preview_list:
            zipf.writestr(item["file_name"], item["content"])
    
    # 重置缓冲区指针
    zip_buffer.seek(0)
    
    return zip_buffer


def get_templates(tpl_category: str) -> List[Dict[str, str]]:
    """
    获取模板列表
    """
    # 模拟模板列表
    templates = [
        {
            "template_name": "model.py.vm",
            "template_content": """from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.database import Base


class ${ClassName}(Base):
    """${functionName}表"""
    __tablename__ = "${tableName}"
    
#foreach ($column in $columns)
    ${column.javaField} = Column(${column.javaType}#if(${column.isPk} == "1"), primary_key=True#end#if(${column.isIncrement} == "1"), autoincrement=True#end, comment="${column.columnComment}")
#end
"""
        },
        {
            "template_name": "schema.py.vm",
            "template_content": """from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ${ClassName}Base(BaseModel):
    """${functionName}基础模型"""
#foreach ($column in $columns)
#if($column.javaField != "createBy" && $column.javaField != "createTime" && $column.javaField != "updateBy" && $column.javaField != "updateTime" && $column.javaField != "remark")
    ${column.javaField}: #if($column.isRequired != "1")Optional[${column.javaType}]#else${column.javaType}#end = Field(#if($column.isRequired == "1")...#else None#end, description="${column.columnComment}")
#end
#end


class ${ClassName}Create(${ClassName}Base):
    """创建${functionName}请求模型"""
    pass


class ${ClassName}Update(${ClassName}Base):
    """更新${functionName}请求模型"""
#foreach ($column in $columns)
#if($column.isPk == "1")
    ${column.javaField}: ${column.javaType} = Field(..., description="${column.columnComment}")
#end
#end


class ${ClassName}Info(${ClassName}Base):
    """${functionName}信息响应模型"""
#foreach ($column in $columns)
#if($column.isPk == "1")
    ${column.javaField}: ${column.javaType} = Field(..., description="${column.columnComment}")
#end
#end
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class ${ClassName}Query(BaseModel):
    """${functionName}查询参数模型"""
#foreach ($column in $columns)
#if($column.isQuery == "1")
    ${column.javaField}: Optional[#if($column.javaType=="String")str#else${column.javaType}#end] = Field(None, description="${column.columnComment}")
#end
#end
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")
"""
        },
        {
            "template_name": "service.py.vm",
            "template_content": """from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.${moduleName}.${businessName} import ${ClassName}
from app.domain.schemas.${moduleName}.${businessName} import ${ClassName}Create, ${ClassName}Update, ${ClassName}Query
from app.common.exception import NotFound


def get_${className}(db: Session, ${pkColumn.javaField}: ${pkColumn.javaType}) -> Optional[${ClassName}]:
    """
    根据${pkColumn.columnComment}获取${functionName}信息
    """
    return db.query(${ClassName}).filter(${ClassName}.${pkColumn.javaField} == ${pkColumn.javaField}).first()


def get_${className}s(
    db: Session, 
    params: ${ClassName}Query
) -> Tuple[List[${ClassName}], int]:
    """
    获取${functionName}列表(分页查询)
    """
    query = db.query(${ClassName})
    
    # 构建查询条件
#foreach ($column in $columns)
#if($column.isQuery == "1")
    if params.${column.javaField}:
#if($column.queryType == "EQ")
        query = query.filter(${ClassName}.${column.javaField} == params.${column.javaField})
#elseif($column.queryType == "NE")
        query = query.filter(${ClassName}.${column.javaField} != params.${column.javaField})
#elseif($column.queryType == "GT")
        query = query.filter(${ClassName}.${column.javaField} > params.${column.javaField})
#elseif($column.queryType == "GTE")
        query = query.filter(${ClassName}.${column.javaField} >= params.${column.javaField})
#elseif($column.queryType == "LT")
        query = query.filter(${ClassName}.${column.javaField} < params.${column.javaField})
#elseif($column.queryType == "LTE")
        query = query.filter(${ClassName}.${column.javaField} <= params.${column.javaField})
#elseif($column.queryType == "LIKE")
        query = query.filter(${ClassName}.${column.javaField}.like(f"%{params.${column.javaField}}%"))
#end
#end
#end
    if params.begin_time and params.end_time:
        query = query.filter(
            ${ClassName}.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    ${className}s = query.order_by(${ClassName}.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ${className}s, total


def create_${className}(
    db: Session, 
    ${className}_data: ${ClassName}Create
) -> ${ClassName}:
    """
    创建${functionName}
    """
    # 创建${functionName}对象
    db_${className} = ${ClassName}(**${className}_data.dict())
    
    # 保存${functionName}信息
    db.add(db_${className})
    db.commit()
    db.refresh(db_${className})
    
    return db_${className}


def update_${className}(
    db: Session, 
    ${pkColumn.javaField}: ${pkColumn.javaType}, 
    ${className}_data: ${ClassName}Update
) -> Optional[${ClassName}]:
    """
    更新${functionName}信息
    """
    # 获取${functionName}信息
    db_${className} = get_${className}(db, ${pkColumn.javaField})
    if not db_${className}:
        raise NotFound(f"${functionName}ID {${pkColumn.javaField}} 不存在")
    
    # 更新${functionName}基本信息
    for key, value in ${className}_data.dict(exclude={"${pkColumn.javaField}"}).items():
        setattr(db_${className}, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_${className})
    
    return db_${className}


def delete_${className}(db: Session, ${pkColumn.javaField}: ${pkColumn.javaType}) -> bool:
    """
    删除${functionName}
    """
    # 获取${functionName}信息
    db_${className} = get_${className}(db, ${pkColumn.javaField})
    if not db_${className}:
        raise NotFound(f"${functionName}ID {${pkColumn.javaField}} 不存在")
    
    # 删除${functionName}
    db.delete(db_${className})
    db.commit()
    
    return True
"""
        },
        {
            "template_name": "api.py.vm",
            "template_content": """from typing import List
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.schemas.${moduleName}.${businessName} import ${ClassName}Create, ${ClassName}Update, ${ClassName}Query
from app.common.response import success, error, page
from app.service.${moduleName}.${businessName}_service import (
    get_${className}, get_${className}s, create_${className}, update_${className}, delete_${className}
)

router = APIRouter()


@router.get("/list", summary="获取${functionName}列表")
async def get_${className}_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: ${ClassName}Query = Depends(),
):
    """
    获取${functionName}列表（分页查询）
    """
    try:
        ${className}s, total = get_${className}s(db, params)
        # 转换为前端格式
        ${className}_list = [
            {
#foreach ($column in $columns)
#if($column.isList == "1")
                "${column.javaField}": ${className}.${column.javaField},
#end
#end
                "create_time": ${className}.create_time
            }
            for ${className} in ${className}s
        ]
        return page(rows=${className}_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{${pkColumn.javaField}}", summary="获取${functionName}详情")
async def get_${className}_info(
    ${pkColumn.javaField}: ${pkColumn.javaType} = Path(..., description="${pkColumn.columnComment}"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取${functionName}详情
    """
    try:
        ${className} = get_${className}(db, ${pkColumn.javaField})
        if not ${className}:
            return error(msg="${functionName}不存在", code=404)
        
        # 转换为前端格式
        ${className}_info = {
#foreach ($column in $columns)
            "${column.javaField}": ${className}.${column.javaField},
#end
        }
        
        return success(data=${className}_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加${functionName}")
async def add_${className}(
    ${className}_data: ${ClassName}Create = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加${functionName}
    """
    try:
        ${className} = create_${className}(db, ${className}_data)
        return success(msg="${functionName}添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改${functionName}")
async def edit_${className}(
    ${className}_data: ${ClassName}Update = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改${functionName}
    """
    try:
        ${className} = update_${className}(db, ${className}_data.${pkColumn.javaField}, ${className}_data)
        return success(msg="${functionName}修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{${pkColumn.javaField}}", summary="删除${functionName}")
async def remove_${className}(
    ${pkColumn.javaField}: ${pkColumn.javaType} = Path(..., description="${pkColumn.columnComment}"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除${functionName}
    """
    try:
        result = delete_${className}(db, ${pkColumn.javaField})
        return success(msg="${functionName}删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))
"""
        }
    ]
    
    return templates


def get_file_name(template_name: str, gen_table: GenTable) -> str:
    """
    获取文件名
    """
    # 替换变量
    file_name = template_name.replace(".vm", "")
    class_name = gen_table.class_name
    business_name = gen_table.business_name
    module_name = gen_table.module_name
    
    if file_name == "model.py":
        return f"app/domain/models/{module_name}/{business_name}.py"
    elif file_name == "schema.py":
        return f"app/domain/schemas/{module_name}/{business_name}.py"
    elif file_name == "service.py":
        return f"app/service/{module_name}/{business_name}_service.py"
    elif file_name == "api.py":
        return f"app/api/{module_name}/{business_name}.py"
    
    return file_name


def generate_code(template_content: str, gen_table: GenTable, gen_columns: List[GenTableColumn]) -> str:
    """
    生成代码
    """
    # 构建变量
    variables = {
        "tableName": gen_table.table_name,
        "ClassName": gen_table.class_name,
        "className": gen_table.class_name[0].lower() + gen_table.class_name[1:],
        "functionName": gen_table.function_name,
        "businessName": gen_table.business_name,
        "moduleName": gen_table.module_name,
        "packageName": gen_table.package_name,
        "author": gen_table.function_author,
        "columns": gen_columns,
        "pkColumn": next((col for col in gen_columns if col.is_pk == "1"), None)
    }
    
    # 简单的模板引擎
    content = template_content
    
    # 替换变量
    for key, value in variables.items():
        if isinstance(value, str):
            content = content.replace(f"${{{key}}}", value)
    
    # 处理循环和条件
    # 这里只是一个简单的实现，实际上需要更复杂的模板引擎
    # 处理foreach
    import re
    
    # 处理foreach循环
    while True:
        foreach_match = re.search(r'#foreach \(\$(\w+) in \$(\w+)\)(.*?)#end', content, re.DOTALL)
        if not foreach_match:
            break
        
        item_var, list_var, loop_content = foreach_match.groups()
        if list_var in variables and isinstance(variables[list_var], list):
            replacement = ""
            for item in variables[list_var]:
                item_content = loop_content
                for attr_name in dir(item):
                    if not attr_name.startswith('_') and not callable(getattr(item, attr_name)):
                        item_content = item_content.replace(f"${{{item_var}.{attr_name}}}", str(getattr(item, attr_name)))
                replacement += item_content
            
            content = content.replace(foreach_match.group(0), replacement)
        else:
            content = content.replace(foreach_match.group(0), "")
    
    # 处理if条件
    while True:
        if_match = re.search(r'#if\((.*?)\)(.*?)(?:#else(.*?))?#end', content, re.DOTALL)
        if not if_match:
            break
        
        condition, if_content, else_content = if_match.groups()
        if else_content is None:
            else_content = ""
        
        # 简单地评估条件
        try:
            # 将变量替换为它们的值
            eval_condition = condition
            for key, value in variables.items():
                if isinstance(value, str):
                    eval_condition = eval_condition.replace(f"${{{key}}}", f'"{value}"')
            
            # 替换列对象的属性
            for col in variables.get("columns", []):
                for attr_name in dir(col):
                    if not attr_name.startswith('_') and not callable(getattr(col, attr_name)):
                        eval_condition = eval_condition.replace(f"${item_var}.{attr_name}", f'"{getattr(col, attr_name)}"')
            
            # 评估条件
            result = eval(eval_condition)
            if result:
                content = content.replace(if_match.group(0), if_content)
            else:
                content = content.replace(if_match.group(0), else_content)
        except:
            # 如果评估失败，则返回空字符串
            content = content.replace(if_match.group(0), "")
    
    return content


def get_java_type(column_type: str) -> str:
    """
    获取Java类型
    """
    if "int" in column_type:
        return "Integer"
    elif "bigint" in column_type:
        return "Integer"
    elif "float" in column_type or "double" in column_type or "decimal" in column_type:
        return "Float"
    elif "datetime" in column_type or "timestamp" in column_type:
        return "DateTime"
    elif "date" in column_type:
        return "Date"
    elif "time" in column_type:
        return "Time"
    elif "bool" in column_type:
        return "Boolean"
    else:
        return "String"


def convert_to_java_field(column_name: str) -> str:
    """
    转换列名为Java字段名（驼峰命名）
    """
    words = column_name.split('_')
    result = words[0].lower()
    for word in words[1:]:
        result += word.capitalize()
    return result


def convert_to_class_name(table_name: str) -> str:
    """
    转换表名为类名（驼峰命名）
    """
    # 去掉前缀
    if table_name.startswith("t_"):
        table_name = table_name[2:]
    elif table_name.startswith("sys_"):
        table_name = table_name[4:]
    
    words = table_name.split('_')
    result = ""
    for word in words:
        if word:
            result += word.capitalize()
    return result


def get_business_name(table_name: str) -> str:
    """
    获取业务名
    """
    # 去掉前缀
    if table_name.startswith("t_"):
        table_name = table_name[2:]
    elif table_name.startswith("sys_"):
        table_name = table_name[4:]
    
    return table_name 