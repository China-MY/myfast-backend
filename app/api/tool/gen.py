from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response, StreamingResponse
import io
import zipfile

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.tool.gen_table import GenTable, GenTableColumn
from app.domain.schemas.tool.gen_table import (
    GenTableCreate, GenTableUpdate, GenTableInfo, GenTableQuery,
    GenTableColumnCreate, GenTableColumnUpdate, GenTableColumnInfo,
    ImportTableQuery, GenPreviewItem
)
from app.common.response import success, error, page
from app.service.tool.gen_service import (
    get_gen_tables, get_gen_table_info, get_db_table_list, import_gen_table,
    update_gen_table, delete_gen_tables, preview_code, download_code, generate_code
)

router = APIRouter()


@router.get("/list", summary="获取代码生成列表")
async def get_table_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: GenTableQuery = Depends()
):
    """
    获取代码生成列表
    """
    try:
        tables, total = get_gen_tables(db, params)
        table_list = []
        for table in tables:
            table_list.append({
                "table_id": table.table_id,
                "table_name": table.table_name,
                "table_comment": table.table_comment,
                "class_name": table.class_name,
                "tpl_category": table.tpl_category,
                "package_name": table.package_name,
                "module_name": table.module_name,
                "business_name": table.business_name,
                "function_name": table.function_name,
                "function_author": table.function_author,
                "create_time": table.create_time,
                "update_time": table.update_time,
            })
        return page(rows=table_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{table_id}", summary="获取代码生成详细信息")
async def get_table_info(
    table_id: int = Path(..., description="表ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    获取代码生成详细信息
    """
    try:
        table, columns = get_gen_table_info(db, table_id)
        if not table:
            return error(msg="表不存在", code=404)
        
        # 构建表信息
        table_info = {
            "table_id": table.table_id,
            "table_name": table.table_name,
            "table_comment": table.table_comment,
            "sub_table_name": table.sub_table_name,
            "sub_table_fk_name": table.sub_table_fk_name,
            "class_name": table.class_name,
            "tpl_category": table.tpl_category,
            "package_name": table.package_name,
            "module_name": table.module_name,
            "business_name": table.business_name,
            "function_name": table.function_name,
            "function_author": table.function_author,
            "gen_type": table.gen_type,
            "gen_path": table.gen_path,
            "options": table.options,
            "remark": table.remark,
            "create_time": table.create_time,
            "update_time": table.update_time,
            "columns": []
        }
        
        # 添加列信息
        for column in columns:
            table_info["columns"].append({
                "column_id": column.column_id,
                "table_id": column.table_id,
                "column_name": column.column_name,
                "column_comment": column.column_comment,
                "column_type": column.column_type,
                "java_type": column.java_type,
                "java_field": column.java_field,
                "is_pk": column.is_pk,
                "is_increment": column.is_increment,
                "is_required": column.is_required,
                "is_insert": column.is_insert,
                "is_edit": column.is_edit,
                "is_list": column.is_list,
                "is_query": column.is_query,
                "query_type": column.query_type,
                "html_type": column.html_type,
                "dict_type": column.dict_type,
                "sort": column.sort
            })
        
        return success(data=table_info)
    except Exception as e:
        return error(msg=str(e))


@router.get("/db/list", summary="获取数据库表列表")
async def get_db_tables(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: ImportTableQuery = Depends()
):
    """
    获取数据库表列表
    """
    try:
        tables, total = get_db_table_list(db, params)
        return page(rows=tables, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.post("/importTable", summary="导入表结构")
async def import_table(
    tables: List[str] = Body(..., description="表名列表"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    导入表结构
    """
    try:
        import_gen_table(db, tables, current_user.user_name)
        return success(msg="导入成功")
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改代码生成信息")
async def update_table(
    table_data: GenTableUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    修改代码生成信息
    """
    try:
        update_gen_table(db, table_data, current_user.user_name)
        return success(msg="修改成功")
    except Exception as e:
        return error(msg=str(e))


@router.delete("/delete/{ids}", summary="删除代码生成")
async def delete_tables(
    ids: str = Path(..., description="表ID，多个以逗号分隔"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    删除代码生成
    """
    try:
        table_ids = [int(x) for x in ids.split(",")]
        delete_gen_tables(db, table_ids)
        return success(msg="删除成功")
    except Exception as e:
        return error(msg=str(e))


@router.get("/preview/{table_id}", summary="预览代码")
async def preview_table_code(
    table_id: int = Path(..., description="表ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    预览代码
    """
    try:
        preview_data = preview_code(db, table_id)
        return success(data=preview_data)
    except Exception as e:
        return error(msg=str(e))


@router.get("/download/{table_id}", summary="下载代码")
async def download_table_code(
    table_id: int = Path(..., description="表ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    下载代码
    """
    try:
        # 获取生成代码的字节流
        code_bytes = download_code(db, table_id)
        
        # 创建响应
        return StreamingResponse(
            io.BytesIO(code_bytes),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=gen_code_{table_id}.zip"
            }
        )
    except Exception as e:
        return error(msg=str(e))


@router.post("/generate/{table_id}", summary="生成代码")
async def gen_code(
    table_id: int = Path(..., description="表ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
):
    """
    生成代码（自定义路径）
    """
    try:
        result = generate_code(db, table_id)
        return success(msg="生成成功", data=result)
    except Exception as e:
        return error(msg=str(e)) 