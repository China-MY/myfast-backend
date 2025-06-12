from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GenTable(Base):
    """
    代码生成业务表
    """
    __tablename__ = "gen_table"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_name = Column(String(200), nullable=False, comment="表名称")
    table_comment = Column(String(500), nullable=True, comment="表描述")
    class_name = Column(String(100), nullable=True, comment="类名称")
    package_name = Column(String(100), nullable=True, default="app.models", comment="生成包路径")
    module_name = Column(String(30), nullable=True, comment="生成模块名")
    business_name = Column(String(30), nullable=True, comment="生成业务名")
    function_name = Column(String(50), nullable=True, comment="生成功能名")
    function_author = Column(String(50), nullable=True, comment="生成功能作者")
    tpl_category = Column(String(20), nullable=True, default="crud", comment="使用的模板（crud单表操作 tree树表操作）")
    options = Column(String(1000), nullable=True, comment="其它生成选项")
    remark = Column(String(500), nullable=True, comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联字段
    columns = relationship("GenTableColumn", back_populates="table", cascade="all, delete-orphan")

class GenTableColumn(Base):
    """
    代码生成业务表字段
    """
    __tablename__ = "gen_table_column"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("gen_table.id"), nullable=False, comment="归属表编号")
    column_name = Column(String(200), nullable=False, comment="列名称")
    column_comment = Column(String(500), nullable=True, comment="列描述")
    column_type = Column(String(100), nullable=True, comment="列类型")
    python_type = Column(String(500), nullable=True, comment="Python类型")
    field_name = Column(String(200), nullable=True, comment="字段名")
    is_pk = Column(String(1), nullable=True, default="0", comment="是否主键（1是）")
    is_increment = Column(String(1), nullable=True, default="0", comment="是否自增（1是）")
    is_required = Column(String(1), nullable=True, default="0", comment="是否必填（1是）")
    is_insert = Column(String(1), nullable=True, default="0", comment="是否为插入字段（1是）")
    is_edit = Column(String(1), nullable=True, default="0", comment="是否编辑字段（1是）")
    is_list = Column(String(1), nullable=True, default="0", comment="是否列表字段（1是）")
    is_query = Column(String(1), nullable=True, default="0", comment="是否查询字段（1是）")
    query_type = Column(String(200), nullable=True, default="EQ", comment="查询方式（等于、不等于、大于、小于、范围）")
    html_type = Column(String(200), nullable=True, comment="显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）")
    dict_type = Column(String(200), nullable=True, comment="字典类型")
    sort = Column(Integer, nullable=True, comment="排序")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联字段
    table = relationship("GenTable", back_populates="columns") 