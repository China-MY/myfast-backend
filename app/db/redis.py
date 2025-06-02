import redis
from app.config import settings

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)

# 获取Redis客户端
def get_redis():
    return redis_client 