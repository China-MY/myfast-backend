from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.dict_type import SysDictType
from app.domain.models.system.dict_data import SysDictData
from app.domain.schemas.system.dict_type import DictTypeCreate, DictTypeUpdate, DictTypeInfo, DictTypeQuery
from app.domain.schemas.system.dict_data import DictDataCreate, DictDataUpdate, DictDataInfo, DictDataQuery
from app.common.exception import NotFound


# ========== 字典类型管理 ==========

def get_dict_type(db: Session, dict_id: int) -> Optional[SysDictType]:
    """
    根据字典类型ID获取字典类型信息
    """
    return db.query(SysDictType).filter(
        SysDictType.dict_id == dict_id,
        SysDictType.del_flag == "0"
    ).first()


def get_dict_type_by_type(db: Session, dict_type: str) -> Optional[SysDictType]:
    """
    根据字典类型获取字典类型信息
    """
    return db.query(SysDictType).filter(
        SysDictType.dict_type == dict_type,
        SysDictType.del_flag == "0"
    ).first()


def get_dict_types(
    db: Session, 
    params: DictTypeQuery
) -> Tuple[List[SysDictType], int]:
    """
    获取字典类型列表（分页查询）
    """
    query = db.query(SysDictType).filter(SysDictType.del_flag == "0")
    
    # 构建查询条件
    if params.dict_name:
        query = query.filter(SysDictType.dict_name.like(f"%{params.dict_name}%"))
    if params.dict_type:
        query = query.filter(SysDictType.dict_type.like(f"%{params.dict_type}%"))
    if params.status:
        query = query.filter(SysDictType.status == params.status)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysDictType.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    dict_types = query.order_by(SysDictType.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return dict_types, total


def create_dict_type(
    db: Session, 
    dict_type_data: DictTypeCreate
) -> SysDictType:
    """
    创建字典类型
    """
    # 检查字典类型是否已存在
    if get_dict_type_by_type(db, dict_type_data.dict_type):
        raise ValueError(f"字典类型 {dict_type_data.dict_type} 已存在")
    
    # 创建字典类型对象
    db_dict_type = SysDictType(
        dict_name=dict_type_data.dict_name,
        dict_type=dict_type_data.dict_type,
        status=dict_type_data.status,
        remark=dict_type_data.remark
    )
    
    # 保存字典类型信息
    db.add(db_dict_type)
    db.commit()
    db.refresh(db_dict_type)
    
    return db_dict_type


def update_dict_type(
    db: Session, 
    dict_id: int, 
    dict_type_data: DictTypeUpdate
) -> Optional[SysDictType]:
    """
    更新字典类型信息
    """
    # 获取字典类型信息
    db_dict_type = get_dict_type(db, dict_id)
    if not db_dict_type:
        raise NotFound(f"字典类型ID {dict_id} 不存在")
    
    # 检查字典类型是否已存在（如果修改了字典类型）
    if db_dict_type.dict_type != dict_type_data.dict_type and get_dict_type_by_type(db, dict_type_data.dict_type):
        raise ValueError(f"字典类型 {dict_type_data.dict_type} 已存在")
    
    # 更新字典类型基本信息
    for key, value in dict_type_data.dict(exclude={"dict_id"}).items():
        if value is not None:
            setattr(db_dict_type, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_dict_type)
    
    return db_dict_type


def delete_dict_type(db: Session, dict_id: int) -> bool:
    """
    删除字典类型（逻辑删除）
    """
    # 获取字典类型信息
    db_dict_type = get_dict_type(db, dict_id)
    if not db_dict_type:
        raise NotFound(f"字典类型ID {dict_id} 不存在")
    
    # 检查是否有关联的字典数据
    has_dict_data = db.query(SysDictData).filter(
        SysDictData.dict_type == db_dict_type.dict_type,
        SysDictData.del_flag == "0"
    ).first() is not None
    
    if has_dict_data:
        raise ValueError(f"字典类型已分配，不能删除")
    
    # 逻辑删除
    db_dict_type.del_flag = "2"
    db.commit()
    
    return True


# ========== 字典数据管理 ==========

def get_dict_data(db: Session, dict_code: int) -> Optional[SysDictData]:
    """
    根据字典数据ID获取字典数据信息
    """
    return db.query(SysDictData).filter(
        SysDictData.dict_code == dict_code,
        SysDictData.del_flag == "0"
    ).first()


def get_dict_datas(
    db: Session, 
    params: DictDataQuery
) -> Tuple[List[SysDictData], int]:
    """
    获取字典数据列表（分页查询）
    """
    query = db.query(SysDictData).filter(SysDictData.del_flag == "0")
    
    # 构建查询条件
    if params.dict_type:
        query = query.filter(SysDictData.dict_type == params.dict_type)
    if params.dict_label:
        query = query.filter(SysDictData.dict_label.like(f"%{params.dict_label}%"))
    if params.status:
        query = query.filter(SysDictData.status == params.status)
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    dict_datas = query.order_by(SysDictData.dict_sort.asc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return dict_datas, total


def get_dict_datas_by_type(db: Session, dict_type: str) -> List[SysDictData]:
    """
    根据字典类型获取字典数据列表
    """
    return db.query(SysDictData).filter(
        SysDictData.dict_type == dict_type,
        SysDictData.status == "0",
        SysDictData.del_flag == "0"
    ).order_by(SysDictData.dict_sort.asc()).all()


def create_dict_data(
    db: Session, 
    dict_data_data: DictDataCreate
) -> SysDictData:
    """
    创建字典数据
    """
    # 检查字典类型是否存在
    if not get_dict_type_by_type(db, dict_data_data.dict_type):
        raise ValueError(f"字典类型 {dict_data_data.dict_type} 不存在")
    
    # 创建字典数据对象
    db_dict_data = SysDictData(
        dict_sort=dict_data_data.dict_sort,
        dict_label=dict_data_data.dict_label,
        dict_value=dict_data_data.dict_value,
        dict_type=dict_data_data.dict_type,
        css_class=dict_data_data.css_class,
        list_class=dict_data_data.list_class,
        is_default=dict_data_data.is_default,
        status=dict_data_data.status,
        remark=dict_data_data.remark
    )
    
    # 保存字典数据信息
    db.add(db_dict_data)
    db.commit()
    db.refresh(db_dict_data)
    
    return db_dict_data


def update_dict_data(
    db: Session, 
    dict_code: int, 
    dict_data_data: DictDataUpdate
) -> Optional[SysDictData]:
    """
    更新字典数据信息
    """
    # 获取字典数据信息
    db_dict_data = get_dict_data(db, dict_code)
    if not db_dict_data:
        raise NotFound(f"字典数据ID {dict_code} 不存在")
    
    # 检查字典类型是否存在（如果修改了字典类型）
    if db_dict_data.dict_type != dict_data_data.dict_type and not get_dict_type_by_type(db, dict_data_data.dict_type):
        raise ValueError(f"字典类型 {dict_data_data.dict_type} 不存在")
    
    # 更新字典数据基本信息
    for key, value in dict_data_data.dict(exclude={"dict_code"}).items():
        if value is not None:
            setattr(db_dict_data, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_dict_data)
    
    return db_dict_data


def delete_dict_data(db: Session, dict_code: int) -> bool:
    """
    删除字典数据（逻辑删除）
    """
    # 获取字典数据信息
    db_dict_data = get_dict_data(db, dict_code)
    if not db_dict_data:
        raise NotFound(f"字典数据ID {dict_code} 不存在")
    
    # 逻辑删除
    db_dict_data.del_flag = "2"
    db.commit()
    
    return True 