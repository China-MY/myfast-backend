from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class GenTable(Base):
    """代码生成业务表"""
    __tablename__ = "gen_table"
    
    table_id = Column(Integer, primary_key=True, autoincrement=True, comment="编号")
    table_name = Column(String(200), default="", comment="表名称")
    table_comment = Column(String(500), default="", comment="表描述")
    sub_table_name = Column(String(64), default="", comment="关联子表的表名")
    sub_table_fk_name = Column(String(64), default="", comment="子表关联的外键名")
    class_name = Column(String(100), default="", comment="实体类名称")
    tpl_category = Column(String(200), default="crud", comment="使用的模板（crud单表操作 tree树表操作）")
    package_name = Column(String(100), default="", comment="生成包路径")
    module_name = Column(String(30), default="", comment="生成模块名")
    business_name = Column(String(30), default="", comment="生成业务名")
    function_name = Column(String(50), default="", comment="生成功能名")
    function_author = Column(String(50), default="", comment="生成功能作者")
    gen_type = Column(String(1), default="0", comment="生成代码方式（0zip压缩包 1自定义路径）")
    gen_path = Column(String(200), default="/", comment="生成路径（不填默认项目路径）")
    options = Column(String(1000), default="", comment="其它生成选项")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    remark = Column(String(500), default="", comment="备注")
    
    # 关联关系
    columns = relationship("GenTableColumn", back_populates="table", cascade="all, delete-orphan")


class GenTableColumn(Base):
    """代码生成业务表字段"""
    __tablename__ = "gen_table_column"
    
    column_id = Column(Integer, primary_key=True, autoincrement=True, comment="编号")
    table_id = Column(Integer, comment="归属表编号")
    column_name = Column(String(200), comment="列名称")
    column_comment = Column(String(500), default="", comment="列描述")
    column_type = Column(String(100), comment="列类型")
    java_type = Column(String(500), comment="Java类型")
    java_field = Column(String(200), comment="Java字段名")
    is_pk = Column(String(1), comment="是否主键（1是）")
    is_increment = Column(String(1), comment="是否自增（1是）")
    is_required = Column(String(1), comment="是否必填（1是）")
    is_insert = Column(String(1), comment="是否为插入字段（1是）")
    is_edit = Column(String(1), comment="是否编辑字段（1是）")
    is_list = Column(String(1), comment="是否列表字段（1是）")
    is_query = Column(String(1), comment="是否查询字段（1是）")
    query_type = Column(String(200), default="EQ", comment="查询方式（等于、不等于、大于、小于、范围）")
    html_type = Column(String(200), comment="显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）")
    dict_type = Column(String(200), default="", comment="字典类型")
    sort = Column(Integer, comment="排序")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    table = relationship("GenTable", back_populates="columns") 