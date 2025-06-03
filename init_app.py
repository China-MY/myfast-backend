import logging

from app.db.init_db import init_db
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """
    初始化应用
    """
    db = SessionLocal()
    try:
        logger.info("创建初始数据")
        init_db(db)
        logger.info("初始数据创建成功")
    finally:
        db.close()


def main() -> None:
    """
    主函数
    """
    logger.info("初始化应用")
    init()
    logger.info("应用初始化完成")


if __name__ == "__main__":
    main() 