import redis
from app.core.config import settings

# 创建Redis客户端连接
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# 检查Redis连接函数
def check_redis_connection():
    try:
        # 尝试ping Redis服务器
        redis_client.ping()
        return True
    except redis.exceptions.ConnectionError:
        return False 