from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, check_permissions
from app.schemas.utils.common import ResponseModel
from app.service.data_monitor import data_monitor_service

router = APIRouter()


@router.get("/db", response_model=ResponseModel[Dict], summary="获取数据库监控信息", description="获取数据库基本监控信息")
def get_db_info(
    db: Session = Depends(get_db),
    _: bool = Depends(check_permissions(["monitor:data:list"]))
) -> Any:
    """
    获取数据库基本监控信息
    """
    db_info = data_monitor_service.get_db_info(db)
    return ResponseModel[Dict](data=db_info)


@router.get("/tables", response_model=ResponseModel[List[Dict]], summary="获取数据库表信息", description="获取数据库所有表信息")
def get_table_info(
    db: Session = Depends(get_db),
    _: bool = Depends(check_permissions(["monitor:data:list"]))
) -> Any:
    """
    获取数据库所有表信息
    """
    tables = data_monitor_service.get_table_info(db)
    return ResponseModel[List[Dict]](data=tables)


@router.get("/table/{table_name}", response_model=ResponseModel[Dict], summary="获取表详情", description="获取指定表的详细信息")
def get_table_detail(
    *,
    db: Session = Depends(get_db),
    table_name: str,
    _: bool = Depends(check_permissions(["monitor:data:list"]))
) -> Any:
    """
    获取指定表的详细信息
    """
    table_detail = data_monitor_service.get_table_detail(db, table_name=table_name)
    if not table_detail:
        raise HTTPException(status_code=404, detail="表不存在")
    
    return ResponseModel[Dict](data=table_detail) 