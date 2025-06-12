from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import check_permissions
from app.schemas.utils.common import ResponseModel
from app.service.cache import cache_service

router = APIRouter()


@router.get("/info", response_model=ResponseModel[Dict], summary="获取缓存信息", description="获取缓存基本信息")
def get_cache_info(
    _: bool = Depends(check_permissions(["monitor:cache:list"]))
) -> Any:
    """
    获取缓存基本信息
    """
    cache_info = cache_service.get_cache_info()
    return ResponseModel[Dict](data=cache_info)


@router.get("/keys", response_model=ResponseModel[List[str]], summary="获取缓存键名列表", description="获取所有缓存键名列表")
def get_cache_keys(
    _: bool = Depends(check_permissions(["monitor:cache:list"]))
) -> Any:
    """
    获取所有缓存键名列表
    """
    keys = cache_service.get_cache_keys()
    return ResponseModel[List[str]](data=keys)


@router.get("/value/{key}", response_model=ResponseModel, summary="获取缓存值", description="根据键名获取缓存值")
def get_cache_value(
    *,
    key: str,
    _: bool = Depends(check_permissions(["monitor:cache:list"]))
) -> Any:
    """
    根据键名获取缓存值
    """
    value = cache_service.get_cache_value(key)
    if value is None:
        raise HTTPException(status_code=404, detail="缓存键不存在")
    
    return ResponseModel(data=value)


@router.delete("/key/{key}", response_model=ResponseModel, summary="删除缓存", description="删除指定键名的缓存")
def delete_cache(
    *,
    key: str,
    _: bool = Depends(check_permissions(["monitor:cache:remove"]))
) -> Any:
    """
    删除指定键名的缓存
    """
    success = cache_service.delete_cache(key)
    if not success:
        raise HTTPException(status_code=404, detail="缓存键不存在")
    
    return ResponseModel(msg="删除成功")


@router.delete("/clear", response_model=ResponseModel, summary="清空缓存", description="清空所有缓存")
def clear_cache(
    _: bool = Depends(check_permissions(["monitor:cache:remove"]))
) -> Any:
    """
    清空所有缓存
    """
    count = cache_service.clear_all_cache()
    return ResponseModel(data={"count": count}, msg=f"已清除{count}个缓存") 