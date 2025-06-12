import os
import sys
import logging
import pymysql
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_sql_file(file_path):
    """执行SQL文件"""
    try:
        # 从DATABASE_URL解析连接参数
        # 格式: mysql+pymysql://username:password@host:port/database
        db_url = settings.DATABASE_URL
        logger.info(f"数据库URL: {db_url}")
        
        parts = db_url.replace('mysql+pymysql://', '').split('/')
        database = parts[1]
        auth_host = parts[0].split('@')
        host_port = auth_host[1].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        auth = auth_host[0].split(':')
        user = auth[0]
        password = auth[1] if len(auth) > 1 else ''
        
        logger.info(f"连接到数据库: {host}:{port}/{database} 用户名: {user}")
        
        # 连接数据库
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        logger.info("数据库连接成功")
        
        # 读取SQL文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        logger.info(f"读取SQL文件成功，文件大小: {len(sql_content)} 字节")
        
        # 执行SQL语句
        with conn.cursor() as cursor:
            # 拆分SQL语句
            sql_commands = sql_content.split(';')
            logger.info(f"拆分出 {len(sql_commands)} 条SQL语句")
            
            executed = 0
            for i, command in enumerate(sql_commands):
                # 跳过空命令
                if command.strip() == '':
                    continue
                
                try:
                    logger.info(f"执行SQL[{i+1}]: {command[:100]}...")  # 只显示前100个字符
                    cursor.execute(command)
                    executed += 1
                    logger.info(f"SQL[{i+1}] 执行成功")
                except Exception as e:
                    logger.error(f"SQL[{i+1}] 执行失败: {str(e)}")
                    raise
            
            # 提交事务
            conn.commit()
            logger.info(f"事务提交成功，共执行 {executed} 条SQL语句")
        
        logger.info(f"SQL文件 {file_path} 执行成功")
        return True
    except Exception as e:
        logger.error(f"执行SQL文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("数据库连接已关闭")

if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) < 2:
        logger.error("请提供SQL文件路径")
        logger.info("用法: python execute_sql.py <sql_file_path>")
        sys.exit(1)
    
    # 获取SQL文件路径
    sql_file = sys.argv[1]
    logger.info(f"准备执行SQL文件: {sql_file}")
    
    # 检查文件是否存在
    if not os.path.exists(sql_file):
        logger.error(f"SQL文件 {sql_file} 不存在")
        sys.exit(1)
    
    # 执行SQL文件
    if execute_sql_file(sql_file):
        logger.info("SQL执行完成")
        sys.exit(0)
    else:
        logger.error("SQL执行失败")
        sys.exit(1) 