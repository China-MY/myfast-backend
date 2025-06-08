import redis
from app.core.config import settings

# 创建Redis客户端
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=False  # 不自动解码响应，在需要的地方手动解码
)


def get_redis_client():
    """
    获取Redis客户端
    """
    return redis_client 