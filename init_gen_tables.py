import logging
import sys
import os
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import engine
from app.models.tool.gen import GenTable, GenTableColumn
from app.db.base_class import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_gen_tables():
    """初始化代码生成表结构"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 检查表是否已存在
        if 'gen_table' in existing_tables and 'gen_table_column' in existing_tables:
            logger.info("代码生成表已存在，无需创建")
            return True
        
        # 创建表结构
        logger.info("开始创建代码生成表结构...")
        
        # 创建元数据
        metadata = MetaData()
        
        # 从模型创建表
        GenTable.__table__.create(engine, checkfirst=True)
        logger.info("创建表 gen_table 成功")
        
        GenTableColumn.__table__.create(engine, checkfirst=True)
        logger.info("创建表 gen_table_column 成功")
        
        logger.info("代码生成表结构创建成功")
        return True
    except Exception as e:
        logger.error(f"创建代码生成表结构失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("开始初始化代码生成表结构...")
    success = init_gen_tables()
    if success:
        logger.info("初始化完成")
    else:
        logger.error("初始化失败") 