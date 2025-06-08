from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.schemas.server import ServerInfo
from app.schemas.common import ResponseModel
from app.service.server import server_service

router = APIRouter()


@router.get("", response_model=ResponseModel[ServerInfo], summary="获取服务器信息", description="获取服务器基本信息")
def get_server_info(
    _: bool = Depends(check_permissions(["monitor:server:list"]))
) -> Any:
    """
    获取服务器基本信息，包括CPU、内存、磁盘等
    """
    server_info = server_service.get_server_info()
    return ResponseModel[ServerInfo](data=server_info)