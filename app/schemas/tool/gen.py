from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GenTableColumnBase(BaseModel):
    """表字段基础信息"""
    column_name: str = Field(..., description="列名称")
    column_comment: Optional[str] = Field(None, description="列描述")
    column_type: Optional[str] = Field(None, description="列类型")
    python_type: Optional[str] = Field(None, description="Python类型")
    field_name: Optional[str] = Field(None, description="字段名")
    is_pk: Optional[str] = Field("0", description="是否主键（1是）")
    is_increment: Optional[str] = Field("0", description="是否自增（1是）")
    is_required: Optional[str] = Field("0", description="是否必填（1是）")
    is_insert: Optional[str] = Field("0", description="是否为插入字段（1是）")
    is_edit: Optional[str] = Field("0", description="是否编辑字段（1是）")
    is_list: Optional[str] = Field("0", description="是否列表字段（1是）")
    is_query: Optional[str] = Field("0", description="是否查询字段（1是）")
    query_type: Optional[str] = Field("EQ", description="查询方式（等于、不等于、大于、小于、范围）")
    html_type: Optional[str] = Field(None, description="显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）")
    dict_type: Optional[str] = Field(None, description="字典类型")
    sort: Optional[int] = Field(None, description="排序")


class GenTableColumnCreate(GenTableColumnBase):
    """创建表字段信息"""
    table_id: int = Field(..., description="归属表编号")


class GenTableColumnUpdate(GenTableColumnBase):
    """更新表字段信息"""
    pass


class GenTableColumnInDB(GenTableColumnBase):
    """数据库中的表字段信息"""
    id: int
    table_id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenTableBase(BaseModel):
    """表基础信息"""
    table_name: str = Field(..., description="表名称")
    table_comment: Optional[str] = Field(None, description="表描述")
    class_name: Optional[str] = Field(None, description="类名称")
    package_name: Optional[str] = Field("app.models", description="生成包路径")
    module_name: Optional[str] = Field(None, description="生成模块名")
    business_name: Optional[str] = Field(None, description="生成业务名")
    function_name: Optional[str] = Field(None, description="生成功能名")
    function_author: Optional[str] = Field(None, description="生成功能作者")
    tpl_category: Optional[str] = Field("crud", description="使用的模板（crud单表操作 tree树表操作）")
    options: Optional[str] = Field(None, description="其它生成选项")
    remark: Optional[str] = Field(None, description="备注")


class GenTableCreate(GenTableBase):
    """创建表信息"""
    pass


class GenTableUpdate(GenTableBase):
    """更新表信息"""
    pass


class GenTableInDB(GenTableBase):
    """数据库中的表信息"""
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenTableDetail(GenTableInDB):
    """包含字段信息的表详情"""
    columns: List[GenTableColumnInDB] = []


class ImportTableRequest(BaseModel):
    """导入表请求"""
    tables: List[str] = Field(..., description="要导入的表名列表")
    data_source_id: Optional[str] = Field("1", description="数据源ID")


class PreviewCodeItem(BaseModel):
    """代码预览项"""
    file_path: str = Field(..., description="文件路径")
    file_content: str = Field(..., description="文件内容")


class TableListItem(BaseModel):
    """数据库表列表项"""
    table_name: str = Field(..., description="表名")
    table_comment: Optional[str] = Field(None, description="表注释")


class GenCodeRequest(BaseModel):
    """生成代码请求"""
    table_ids: List[int] = Field(..., description="表ID列表")


class PageParams(BaseModel):
    """分页参数"""
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页记录数")


class TableQueryParams(PageParams):
    """表查询参数"""
    table_name: Optional[str] = Field(None, description="表名称")
    table_comment: Optional[str] = Field(None, description="表描述")
    begin_time: Optional[datetime] = Field(None, description="开始日期")
    end_time: Optional[datetime] = Field(None, description="结束日期") 