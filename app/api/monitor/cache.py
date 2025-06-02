from typing import Dict, List, Any
from fastapi import APIRouter, Depends, Body, Path
import time

from app.common.response import success, error
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.core.redis import redis_client, check_redis_connection

router = APIRouter()


@router.get("/info", summary="获取Redis服务信息")
async def get_redis_info(
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取Redis服务器信息
    """
    try:
        # 检查Redis连接是否可用
        if not check_redis_connection():
            return error(msg="Redis服务不可用，请检查Redis服务是否启动")
            
        info = redis_client.info()
        
        # 处理基本信息
        redis_info = {
            "version": info.get("redis_version", "未知"),
            "uptime_in_days": info.get("uptime_in_days", 0),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
            "total_system_memory_human": info.get("total_system_memory_human", "0B"),
            "maxmemory_human": info.get("maxmemory_human", "0B"),
            "maxmemory_policy": info.get("maxmemory_policy", "未设置"),
            "rdb_last_save_time": format_timestamp(info.get("rdb_last_save_time", 0)),
            "rdb_last_bgsave_status": info.get("rdb_last_bgsave_status", "未知"),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            "rejected_connections": info.get("rejected_connections", 0),
            "expired_keys": info.get("expired_keys", 0),
            "evicted_keys": info.get("evicted_keys", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "pubsub_channels": info.get("pubsub_channels", 0),
            "pubsub_patterns": info.get("pubsub_patterns", 0),
            "loading": info.get("loading", 0),
            "databases": get_db_info(info)
        }
        
        return success(data=redis_info)
    except Exception as e:
        return error(msg=f"获取Redis服务器信息失败: {str(e)}")


@router.get("/keys", summary="获取Redis键列表")
async def get_redis_keys(
    current_user: SysUser = Depends(get_current_active_user),
    pattern: str = "*",
    limit: int = 100
):
    """
    获取Redis键列表
    """
    try:
        # 检查Redis连接是否可用
        if not check_redis_connection():
            return error(msg="Redis服务不可用，请检查Redis服务是否启动")
            
        # 获取键列表
        keys = redis_client.keys(pattern)
        total = len(keys)
        
        # 限制返回数量
        keys = keys[:limit]
        
        # 获取键的类型和TTL
        key_info = []
        for key in keys:
            key_type = redis_client.type(key)
            ttl = redis_client.ttl(key)
            
            # 根据键的类型获取大小
            size = get_key_size(key, key_type)
            
            key_info.append({
                "key": key,
                "type": key_type,
                "ttl": ttl,
                "size": size
            })
        
        return success(data={
            "keys": key_info,
            "total": total,
            "pattern": pattern,
            "limit": limit
        })
    except Exception as e:
        return error(msg=f"获取Redis键列表失败: {str(e)}")


@router.get("/key/{key}", summary="获取Redis键值")
async def get_redis_key_value(
    key: str = Path(..., description="键名"),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取Redis键值
    """
    try:
        # 检查Redis连接是否可用
        if not check_redis_connection():
            return error(msg="Redis服务不可用，请检查Redis服务是否启动")
            
        # 检查键是否存在
        if not redis_client.exists(key):
            return error(msg=f"键 {key} 不存在", code=404)
        
        # 获取键的类型
        key_type = redis_client.type(key)
        ttl = redis_client.ttl(key)
        
        # 根据类型获取值
        value = None
        if key_type == "string":
            value = redis_client.get(key)
        elif key_type == "list":
            value = redis_client.lrange(key, 0, -1)
        elif key_type == "set":
            value = list(redis_client.smembers(key))
        elif key_type == "zset":
            value = redis_client.zrange(key, 0, -1, withscores=True)
            value = [{"member": item[0], "score": item[1]} for item in value]
        elif key_type == "hash":
            value = redis_client.hgetall(key)
        
        return success(data={
            "key": key,
            "type": key_type,
            "ttl": ttl,
            "value": value
        })
    except Exception as e:
        return error(msg=f"获取Redis键值失败: {str(e)}")


@router.delete("/key/{key}", summary="删除Redis键")
async def delete_redis_key(
    key: str = Path(..., description="键名"),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除Redis键
    """
    try:
        # 检查Redis连接是否可用
        if not check_redis_connection():
            return error(msg="Redis服务不可用，请检查Redis服务是否启动")
            
        # 检查键是否存在
        if not redis_client.exists(key):
            return error(msg=f"键 {key} 不存在", code=404)
        
        # 删除键
        redis_client.delete(key)
        
        return success(msg=f"键 {key} 删除成功")
    except Exception as e:
        return error(msg=f"删除Redis键失败: {str(e)}")


@router.delete("/flushdb", summary="清空当前数据库")
async def flush_db(
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    清空当前数据库
    """
    try:
        # 检查Redis连接是否可用
        if not check_redis_connection():
            return error(msg="Redis服务不可用，请检查Redis服务是否启动")
            
        # 清空当前数据库
        redis_client.flushdb()
        
        return success(msg="当前数据库已清空")
    except Exception as e:
        return error(msg=f"清空当前数据库失败: {str(e)}")


def format_timestamp(timestamp: int) -> str:
    """
    格式化时间戳为可读字符串
    """
    if not timestamp:
        return "未知"
    
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    return time_str


def get_db_info(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    获取Redis数据库信息
    """
    db_info = []
    for key, value in info.items():
        if key.startswith("db"):
            db_number = key
            keys = value.get("keys", 0)
            expires = value.get("expires", 0)
            db_info.append({
                "name": db_number,
                "keys": keys,
                "expires": expires
            })
    
    return db_info


def get_key_size(key: str, key_type: str) -> int:
    """
    获取键的大小（元素数量）
    """
    try:
        if key_type == "string":
            return len(redis_client.get(key) or "")
        elif key_type == "list":
            return redis_client.llen(key)
        elif key_type == "set":
            return redis_client.scard(key)
        elif key_type == "zset":
            return redis_client.zcard(key)
        elif key_type == "hash":
            return redis_client.hlen(key)
        else:
            return 0
    except Exception:
        return 0 