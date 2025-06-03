import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine, SessionLocal
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """
    初始化数据库，确保表存在且有必要的初始数据
    """
    try:
        # 使用上下文管理器处理会话
        db = SessionLocal()
        try:
            # 检查数据库连接
            logger.info("正在检查数据库连接...")
            db.execute(text("SELECT 1"))
            
            # 检查用户表是否存在
            logger.info("检查系统用户表是否存在...")
            result = db.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'myfast_admin' 
                AND table_name = 'sys_user'
            """))
            
            if result.scalar() == 0:
                logger.warning("数据库表不存在，请先执行SQL初始化脚本")
                return
            
            # 检查是否需要创建管理员用户
            logger.info("检查管理员用户是否存在...")
            result = db.execute(text("SELECT COUNT(*) FROM sys_user WHERE username = 'admin'"))
            
            if result.scalar() == 0:
                logger.info("创建默认管理员用户...")
                hashed_password = get_password_hash("123456")
                db.execute(
                    text("""
                    INSERT INTO sys_user 
                    (dept_id, username, nickname, email, phonenumber, sex, password, status, del_flag, create_by, create_time, remark)
                    VALUES
                    (100, 'admin', '管理员', 'admin@example.com', '15888888888', '0', :password, '0', '0', 'system', NOW(), '系统默认管理员')
                    """),
                    {"password": hashed_password}
                )
                db.commit()
                logger.info("管理员用户创建完成")
            else:
                logger.info("管理员用户已存在")
                
            logger.info("数据库初始化完成")
                
        except SQLAlchemyError as e:
            logger.error(f"数据库初始化过程中出现错误: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise 