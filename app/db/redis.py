import redis
from app.core.config import settings

# Redis客户端连接池
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True  # 自动解码响应
)

def get_redis():
    """获取Redis客户端实例"""
    try:
        # 测试连接是否有效
        redis_client.ping()
        return redis_client
    except redis.ConnectionError:
        # 连接失败则重新连接
        return redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True
        ) 