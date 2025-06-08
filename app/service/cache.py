from typing import Dict, List, Any, Optional
import json
import time

from app.core.redis import redis_client


class CacheService:
    """
    缓存监控服务
    """
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存基本信息
        """
        info = redis_client.info()
        
        # 提取关键信息
        cache_info = {
            "redis_version": info.get("redis_version", ""),
            "uptime_in_days": info.get("uptime_in_days", 0),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", ""),
            "total_memory_human": info.get("total_system_memory_human", ""),
            "used_cpu_sys": info.get("used_cpu_sys", 0),
            "used_cpu_user": info.get("used_cpu_user", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "total_connections_received": info.get("total_connections_received", 0),
            "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            "rejected_connections": info.get("rejected_connections", 0),
            "expired_keys": info.get("expired_keys", 0),
            "evicted_keys": info.get("evicted_keys", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "db_size": self._get_db_size()
        }
        
        return cache_info
    
    def _get_db_size(self) -> int:
        """
        获取数据库大小
        """
        try:
            return redis_client.dbsize()
        except:
            return 0
    
    def get_cache_keys(self, pattern: str = "*") -> List[str]:
        """
        获取所有缓存键名列表
        """
        try:
            keys = redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except:
            return []
    
    def get_cache_value(self, key: str) -> Any:
        """
        根据键名获取缓存值
        """
        if not redis_client.exists(key):
            return None
        
        # 获取键的类型
        key_type = redis_client.type(key)
        if isinstance(key_type, bytes):
            key_type = key_type.decode('utf-8')
        
        # 根据类型获取值
        if key_type == "string":
            value = redis_client.get(key)
            if isinstance(value, bytes):
                try:
                    # 尝试解析为JSON
                    return json.loads(value)
                except:
                    # 解析失败则返回字符串
                    return value.decode('utf-8')
            return value
        elif key_type == "list":
            return redis_client.lrange(key, 0, -1)
        elif key_type == "set":
            return list(redis_client.smembers(key))
        elif key_type == "zset":
            return redis_client.zrange(key, 0, -1, withscores=True)
        elif key_type == "hash":
            return redis_client.hgetall(key)
        else:
            return None
    
    def delete_cache(self, key: str) -> bool:
        """
        删除指定键名的缓存
        """
        if redis_client.exists(key):
            redis_client.delete(key)
            return True
        return False
    
    def clear_all_cache(self) -> int:
        """
        清空所有缓存
        """
        keys = self.get_cache_keys()
        if not keys:
            return 0
        
        count = len(keys)
        redis_client.delete(*keys)
        return count


# 实例化服务
cache_service = CacheService() 