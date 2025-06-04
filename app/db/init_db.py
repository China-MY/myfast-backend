import logging
import os
import pymysql
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models.user import SysUser
from app.models.role import SysRole, sys_role_menu, sys_user_role, sys_role_dept
from app.models.menu import SysMenu
from app.models.dept import SysDept
from app.models.post import SysPost, sys_user_post
from app.utils.password import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    初始化数据库模型
    注意：表结构由SQL文件创建，这里只是注册模型
    """
    # 如果使用SQL文件创建了表，不需要再次创建
    # Base.metadata.create_all(bind=engine)
    logger.info("数据库模型已注册完成")


def init_from_sql(db: Session) -> None:
    """
    从SQL文件初始化数据库
    """
    logger.info("请使用init_database.py脚本从SQL文件初始化数据库")


def check_db_initialized(db: Session) -> bool:
    """
    检查数据库是否已初始化
    """
    try:
        # 检查是否有管理员账户
        admin_user = db.query(SysUser).filter(SysUser.username == "admin").first()
        if admin_user:
            logger.info("数据库已初始化")
            return True
        else:
            logger.info("数据库未初始化")
            return False
    except Exception as e:
        logger.error(f"检查数据库初始化状态出错: {e}")
        return False


def init_data(db: Session) -> None:
    """
    初始化基础数据
    """
    # 检查是否已有数据
    user = db.query(SysUser).filter(SysUser.username == "admin").first()
    if user:
        logger.info("数据已初始化，跳过")
        return
    
    logger.info("开始初始化基础数据...")
    
    # 创建部门
    dept = SysDept(
        dept_id=100,
        parent_id=0,
        ancestors="0",
        dept_name="总公司",
        order_num=0,
        leader="管理员",
        phone="15888888888",
        email="admin@example.com",
        status="0",
        create_by="admin"
    )
    db.add(dept)
    
    # 创建角色
    role = SysRole(
        role_id=1,
        role_name="超级管理员",
        role_key="admin",
        role_sort=1,
        data_scope="1",
        status="0",
        create_by="admin"
    )
    db.add(role)
    
    # 创建用户
    admin = SysUser(
        user_id=1,
        dept_id=100,
        username="admin",
        nickname="管理员",
        password=get_password_hash("123456"),
        email="admin@example.com",
        phonenumber="15888888888",
        sex="0",
        status="0",
        create_by="admin"
    )
    db.add(admin)
    
    # 提交会话
    db.commit()
    
    # 添加用户角色关联
    admin.roles = [role]
    db.commit()
    
    logger.info("基础数据初始化完成") 