from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SysDictData(Base):
    """字典数据表"""
    __tablename__ = "sys_dict_data"
    
    dict_code = Column(Integer, primary_key=True, autoincrement=True, comment="字典编码")
    dict_sort = Column(Integer, default=0, comment="字典排序")
    dict_label = Column(String(100), default="", comment="字典标签")
    dict_value = Column(String(100), default="", comment="字典键值")
    dict_type_id = Column(Integer, ForeignKey("sys_dict_type.dict_id"), comment="字典类型ID")
    dict_type_name = Column(String(100), default="", comment="字典类型")
    css_class = Column(String(100), default="", comment="样式属性（其他样式扩展）")
    list_class = Column(String(100), default="", comment="表格回显样式")
    is_default = Column(String(1), default="N", comment="是否默认（Y是 N否）")
    status = Column(String(1), default="0", comment="状态（0正常 1停用）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    remark = Column(String(500), default="", comment="备注")
    
    # 关联关系
    dict_type = relationship("SysDictType", back_populates="dict_data") 