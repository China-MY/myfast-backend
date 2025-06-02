from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SysDictType(Base):
    """字典类型表"""
    __tablename__ = "sys_dict_type"
    
    dict_id = Column(Integer, primary_key=True, autoincrement=True, comment="字典主键")
    dict_name = Column(String(100), default="", comment="字典名称")
    dict_type = Column(String(100), default="", unique=True, comment="字典类型")
    status = Column(String(1), default="0", comment="状态（0正常 1停用）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    remark = Column(String(500), default="", comment="备注")
    
    # 关联关系
    dict_data = relationship("SysDictData", back_populates="dict_type", cascade="all, delete-orphan") 