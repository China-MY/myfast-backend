from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.config import SysConfig
from app.domain.schemas.system.config import ConfigCreate, ConfigUpdate, ConfigInfo, ConfigQuery
from app.common.exception import NotFound


def get_config(db: Session, config_id: int) -> Optional[SysConfig]:
    """
    根据参数ID获取参数配置信息
    """
    return db.query(SysConfig).filter(
        SysConfig.config_id == config_id,
        SysConfig.del_flag == "0"
    ).first()


def get_config_by_key(db: Session, config_key: str) -> Optional[SysConfig]:
    """
    根据参数键名获取参数配置信息
    """
    return db.query(SysConfig).filter(
        SysConfig.config_key == config_key,
        SysConfig.del_flag == "0"
    ).first()


def get_configs(
    db: Session, 
    params: ConfigQuery
) -> Tuple[List[SysConfig], int]:
    """
    获取参数配置列表（分页查询）
    """
    query = db.query(SysConfig).filter(SysConfig.del_flag == "0")
    
    # 构建查询条件
    if params.config_name:
        query = query.filter(SysConfig.config_name.like(f"%{params.config_name}%"))
    if params.config_key:
        query = query.filter(SysConfig.config_key.like(f"%{params.config_key}%"))
    if params.config_type:
        query = query.filter(SysConfig.config_type == params.config_type)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysConfig.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    configs = query.order_by(SysConfig.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return configs, total


def create_config(
    db: Session, 
    config_data: ConfigCreate
) -> SysConfig:
    """
    创建参数配置
    """
    # 检查参数键名是否已存在
    if get_config_by_key(db, config_data.config_key):
        raise ValueError(f"参数键名 {config_data.config_key} 已存在")
    
    # 创建参数配置对象
    db_config = SysConfig(
        config_name=config_data.config_name,
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        config_type=config_data.config_type,
        remark=config_data.remark
    )
    
    # 保存参数配置信息
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


def update_config(
    db: Session, 
    config_id: int, 
    config_data: ConfigUpdate
) -> Optional[SysConfig]:
    """
    更新参数配置信息
    """
    # 获取参数配置信息
    db_config = get_config(db, config_id)
    if not db_config:
        raise NotFound(f"参数ID {config_id} 不存在")
    
    # 内置参数不允许修改
    if db_config.config_type == "Y":
        raise ValueError("内置参数不允许修改")
    
    # 检查参数键名是否已存在（如果修改了参数键名）
    if db_config.config_key != config_data.config_key and get_config_by_key(db, config_data.config_key):
        raise ValueError(f"参数键名 {config_data.config_key} 已存在")
    
    # 更新参数配置基本信息
    for key, value in config_data.dict(exclude={"config_id"}).items():
        if value is not None:
            setattr(db_config, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_config)
    
    return db_config


def delete_config(db: Session, config_id: int) -> bool:
    """
    删除参数配置（逻辑删除）
    """
    # 获取参数配置信息
    db_config = get_config(db, config_id)
    if not db_config:
        raise NotFound(f"参数ID {config_id} 不存在")
    
    # 内置参数不允许删除
    if db_config.config_type == "Y":
        raise ValueError("内置参数不允许删除")
    
    # 逻辑删除
    db_config.del_flag = "2"
    db.commit()
    
    return True 