from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
import json
from datetime import datetime

from app.api import deps
from app.crud.tool.gen import gen_table, gen_table_column
from app.schemas.tool.gen import (
    GenTableInDB, GenTableCreate, GenTableUpdate, 
    GenTableColumnInDB, GenTableColumnCreate, GenTableColumnUpdate,
    GenTableDetail, TableQueryParams, ImportTableRequest, 
    PreviewCodeItem, GenCodeRequest, TableListItem
)
from app.service.tool.gen_service import gen_service

router = APIRouter()


@router.get("/tables", response_model=List[TableListItem])
def get_db_tables(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    获取数据库表列表
    """
    tables = gen_service.get_db_table_list()
    return tables


@router.post("/import", response_model=List[GenTableInDB])
def import_tables(
    *,
    db: Session = Depends(deps.get_db),
    req: ImportTableRequest,
) -> Any:
    """
    导入表结构
    """
    tables = gen_table.import_tables(db, tables=req.tables)
    return tables


@router.get("/list", response_model=List[GenTableInDB])
def get_table_list(
    db: Session = Depends(deps.get_db),
    table_name: Optional[str] = None,
    table_comment: Optional[str] = None,
    begin_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page_num: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Any:
    """
    获取代码生成表列表
    """
    query = TableQueryParams(
        table_name=table_name,
        table_comment=table_comment,
        begin_time=begin_time,
        end_time=end_time,
        page_num=page_num,
        page_size=page_size
    )
    return gen_table.get_list(db, query=query)


@router.get("/total", response_model=int)
def get_table_total(
    db: Session = Depends(deps.get_db),
    table_name: Optional[str] = None,
    table_comment: Optional[str] = None,
    begin_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Any:
    """
    获取代码生成表总数
    """
    query = TableQueryParams(
        table_name=table_name,
        table_comment=table_comment,
        begin_time=begin_time,
        end_time=end_time
    )
    return gen_table.get_count(db, query=query)


@router.get("/{id}", response_model=GenTableDetail)
def get_table_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
) -> Any:
    """
    获取表详情
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    columns = gen_table_column.get_list_by_table_id(db, table.id)
    
    return GenTableDetail(
        **table.__dict__,
        columns=columns
    )


@router.put("/{id}", response_model=GenTableInDB)
def update_table(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
    obj_in: GenTableUpdate,
) -> Any:
    """
    更新表信息
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    return gen_table.update(db, db_obj=table, obj_in=obj_in)


@router.put("/{id}/columns", response_model=List[GenTableColumnInDB])
def update_table_columns(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
    columns: List[GenTableColumnUpdate],
) -> Any:
    """
    更新表字段信息
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    db_columns = gen_table_column.get_list_by_table_id(db, id)
    
    # 更新字段信息
    for idx, column_in in enumerate(columns):
        if idx < len(db_columns):
            gen_table_column.update(db, db_obj=db_columns[idx], obj_in=column_in)
    
    # 返回更新后的字段列表
    return gen_table_column.get_list_by_table_id(db, id)


@router.delete("/{id}", response_model=GenTableInDB)
def delete_table(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
) -> Any:
    """
    删除表信息
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    return gen_table.remove(db, id=id)


@router.delete("/batch", response_model=List[GenTableInDB])
def batch_delete_tables(
    *,
    db: Session = Depends(deps.get_db),
    ids: List[int] = Body(..., embed=True),
) -> Any:
    """
    批量删除表信息
    """
    return gen_table.remove_batch(db, ids=ids)


@router.get("/{id}/preview", response_model=List[PreviewCodeItem])
def preview_code(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
) -> Any:
    """
    预览代码
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    return gen_service.preview_code(db, id)


@router.get("/{id}/generate")
def generate_code(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0),
    token: str = None,
) -> Any:
    """
    生成代码
    """
    table = gen_table.get(db, id)
    if not table:
        raise HTTPException(status_code=404, detail="表不存在")
    
    try:
        zip_content, zip_filename = gen_service.generate_code(db, id)
        
        # 返回ZIP文件
        headers = {
            "Content-Disposition": f'attachment; filename="{zip_filename}"',
            "Content-Type": "application/zip",
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        return StreamingResponse(
            BytesIO(zip_content),
            media_type="application/zip",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成代码失败: {str(e)}")


@router.post("/batch/generate")
def batch_generate_code(
    *,
    db: Session = Depends(deps.get_db),
    req: GenCodeRequest = None,
    table_ids: str = Form(None),
    token: str = Form(None),
) -> Any:
    """
    批量生成代码
    """
    try:
        # 处理表单提交的情况
        ids_list = []
        if req and req.table_ids:
            ids_list = req.table_ids
        elif table_ids:
            try:
                ids_list = json.loads(table_ids)
            except:
                raise HTTPException(status_code=400, detail="无效的表ID格式")
        
        if not ids_list:
            raise HTTPException(status_code=400, detail="未提供表ID")
            
        zip_content, zip_filename = gen_service.generate_batch_code(db, ids_list)
        
        # 返回ZIP文件
        headers = {
            "Content-Disposition": f'attachment; filename="{zip_filename}"',
            "Content-Type": "application/zip",
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        return StreamingResponse(
            BytesIO(zip_content),
            media_type="application/zip",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成代码失败: {str(e)}") 