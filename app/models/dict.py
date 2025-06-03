from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class DictType(Base):
    __tablename__ = "sys_dict_type"

    dict_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dict_name = Column(String(100), default="")
    dict_type = Column(String(100), default="", unique=True, index=True)
    status = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), nullable=True)

    # 关系定义
    dict_data = relationship("DictData", back_populates="dict_type")

    def __repr__(self):
        return f"<DictType {self.dict_name}>"


class DictData(Base):
    __tablename__ = "sys_dict_data"

    dict_code = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dict_sort = Column(Integer, default=0)
    dict_label = Column(String(100), default="")
    dict_value = Column(String(100), default="")
    dict_type = Column(String(100), ForeignKey("sys_dict_type.dict_type"))
    css_class = Column(String(100), nullable=True)
    list_class = Column(String(100), nullable=True)
    is_default = Column(String(1), default="N")
    status = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), nullable=True)

    # 关系定义
    dict_type_obj = relationship("DictType", back_populates="dict_data")

    def __repr__(self):
        return f"<DictData {self.dict_label}>" 