from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,  # 设为True可以看到执行的SQL语句
    pool_recycle=3600,  # 连接在给定时间后回收
    pool_size=20,  # 连接池大小
    max_overflow=20,  # 超过连接池大小后可允许的连接数
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """
    获取数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 