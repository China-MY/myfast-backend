from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 表字段基础模型
class GenTableColumnBase(BaseModel):
    column_name: str = Field(..., description="列名称")
    column_comment: Optional[str] = Field("", description="列描述")
    column_type: str = Field(..., description="列类型")
    java_type: str = Field(..., description="Java类型")
    java_field: str = Field(..., description="Java字段名")
    is_pk: str = Field("0", description="是否主键（1是）")
    is_increment: str = Field("0", description="是否自增（1是）")
    is_required: str = Field("0", description="是否必填（1是）")
    is_insert: str = Field("0", description="是否为插入字段（1是）")
    is_edit: str = Field("0", description="是否编辑字段（1是）")
    is_list: str = Field("0", description="是否列表字段（1是）")
    is_query: str = Field("0", description="是否查询字段（1是）")
    query_type: str = Field("EQ", description="查询方式（等于、不等于、大于、小于、范围）")
    html_type: str = Field("input", description="显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）")
    dict_type: Optional[str] = Field("", description="字典类型")
    sort: int = Field(0, description="排序")

# 表字段创建模型
class GenTableColumnCreate(GenTableColumnBase):
    table_id: int = Field(..., description="归属表编号")

# 表字段更新模型
class GenTableColumnUpdate(GenTableColumnBase):
    column_id: int = Field(..., description="字段ID")
    table_id: int = Field(..., description="归属表编号")

# 表字段信息模型
class GenTableColumnInfo(GenTableColumnBase):
    column_id: int = Field(..., description="字段ID")
    table_id: int = Field(..., description="归属表编号")
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

# 代码生成表基础模型
class GenTableBase(BaseModel):
    table_name: str = Field(..., description="表名称")
    table_comment: Optional[str] = Field("", description="表描述")
    sub_table_name: Optional[str] = Field("", description="关联子表的表名")
    sub_table_fk_name: Optional[str] = Field("", description="子表关联的外键名")
    class_name: str = Field(..., description="实体类名称")
    tpl_category: str = Field("crud", description="使用的模板（crud单表操作 tree树表操作）")
    package_name: str = Field(..., description="生成包路径")
    module_name: str = Field(..., description="生成模块名")
    business_name: str = Field(..., description="生成业务名")
    function_name: str = Field(..., description="生成功能名")
    function_author: str = Field(..., description="生成功能作者")
    gen_type: str = Field("0", description="生成代码方式（0zip压缩包 1自定义路径）")
    gen_path: Optional[str] = Field("/", description="生成路径（不填默认项目路径）")
    options: Optional[str] = Field("", description="其它生成选项")
    remark: Optional[str] = Field("", description="备注")

# 代码生成表创建模型
class GenTableCreate(GenTableBase):
    pass

# 代码生成表更新模型
class GenTableUpdate(GenTableBase):
    table_id: int = Field(..., description="表ID")

# 代码生成表信息模型
class GenTableInfo(GenTableBase):
    table_id: int = Field(..., description="表ID")
    create_time: datetime = Field(..., description="创建时间")
    columns: List[GenTableColumnInfo] = Field([], description="表字段列表")
    
    class Config:
        from_attributes = True

# 代码生成表查询参数
class GenTableQuery(BaseModel):
    table_name: Optional[str] = Field(None, description="表名称")
    table_comment: Optional[str] = Field(None, description="表描述")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")

# 导入表查询参数
class ImportTableQuery(BaseModel):
    table_name: Optional[str] = Field(None, description="表名称")
    table_comment: Optional[str] = Field(None, description="表描述")
    
# 代码生成预览
class GenPreviewItem(BaseModel):
    file_name: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容") 