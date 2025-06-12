from typing import Dict, List, Any, Optional, Tuple
import os
import shutil
import tempfile
import zipfile
import logging
from datetime import datetime
from sqlalchemy import inspect
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi.encoders import jsonable_encoder

from app.db.session import engine
from app.crud.tool.gen import gen_table, gen_table_column
from app.models.tool.gen import GenTable, GenTableColumn
from app.schemas.tool.gen import GenTableInDB, GenTableColumnInDB, GenTableUpdate, GenTableColumnUpdate, PreviewCodeItem
from app.utils.db_utils import get_db_tables, get_template_context

# 配置日志
logger = logging.getLogger(__name__)

class GenService:
    """代码生成服务"""
    
    def __init__(self):
        # 模板目录
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
        # 确保模板目录存在
        if not os.path.exists(self.template_dir):
            logger.info(f"模板目录不存在，正在创建: {self.template_dir}")
            os.makedirs(self.template_dir)
            # 创建模板子目录
            os.makedirs(os.path.join(self.template_dir, "crud"), exist_ok=True)
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        logger.info(f"代码生成服务初始化完成，模板目录: {self.template_dir}")
    
    def get_db_table_list(self, db_name: str = None) -> List[Dict[str, str]]:
        """获取数据库表列表"""
        inspector = inspect(engine)
        return get_db_tables(inspector)
    
    def preview_code(self, db, table_id: int) -> List[PreviewCodeItem]:
        """预览代码"""
        # 获取表信息
        logger.info(f"开始预览代码生成，表ID: {table_id}")
        table_obj = gen_table.get(db, table_id)
        if not table_obj:
            logger.warning(f"表不存在，ID: {table_id}")
            return []
        
        # 获取表字段信息
        column_objs = gen_table_column.get_list_by_table_id(db, table_id)
        logger.info(f"获取到表 {table_obj.table_name} 的字段数量: {len(column_objs)}")
        
        # 转换为字典
        table_dict = jsonable_encoder(table_obj)
        columns_dict = [jsonable_encoder(col) for col in column_objs]
        
        # 获取模板上下文
        context = get_template_context(table_dict, columns_dict)
        
        # 根据模板类别选择模板
        tpl_category = table_obj.tpl_category or "crud"
        logger.info(f"使用模板类别: {tpl_category}")
        
        # 生成代码
        code_files = []
        
        try:
            # 获取模板文件列表
            template_files = self._get_template_files(tpl_category)
            logger.info(f"找到模板文件数量: {len(template_files)}")
            
            # 如果没有找到模板文件，或者模板文件不完整，创建/补充默认模板
            if not template_files or len(template_files) < 6:  # 完整模板应该有6个文件
                logger.warning(f"未找到模板文件或模板不完整，正在创建/补充默认模板，类别: {tpl_category}")
                self._create_default_templates(tpl_category)
                template_files = self._get_template_files(tpl_category)
                logger.info(f"创建/补充默认模板后，找到模板文件数量: {len(template_files)}")
                if not template_files:
                    # 仍然没有模板，返回错误信息
                    logger.error(f"无法找到或创建模板文件，类别: {tpl_category}")
                    return [PreviewCodeItem(
                        file_path="error.txt",
                        file_content="无法找到模板文件，请检查模板目录"
                    )]
            
            # 渲染每个模板文件
            for template_file in template_files:
                try:
                    logger.info(f"开始渲染模板: {template_file}")
                    # 渲染模板
                    template = self.env.get_template(f"{tpl_category}/{template_file}")
                    content = template.render(**context)
                    
                    # 替换文件名中的变量
                    output_file = self._process_filename(template_file, context)
                    logger.info(f"模板 {template_file} 渲染成功，输出文件: {output_file}")
                    
                    code_files.append(PreviewCodeItem(
                        file_path=output_file,
                        file_content=content
                    ))
                except Exception as e:
                    logger.error(f"模板 {template_file} 渲染失败: {str(e)}", exc_info=True)
                    # 添加错误信息作为文件内容
                    code_files.append(PreviewCodeItem(
                        file_path=template_file,
                        file_content=f"模板渲染失败: {str(e)}"
                    ))
        except Exception as e:
            # 捕获整个过程中的异常
            logger.error(f"代码预览过程中发生异常: {str(e)}", exc_info=True)
            code_files.append(PreviewCodeItem(
                file_path="error.txt",
                file_content=f"代码预览失败: {str(e)}"
            ))
        
        # 确保返回非空列表
        if not code_files:
            logger.warning("未生成任何预览代码文件")
            code_files.append(PreviewCodeItem(
                file_path="info.txt",
                file_content="未能生成预览代码，请检查模板配置"
            ))
        
        logger.info(f"代码预览完成，生成文件数量: {len(code_files)}")
        return code_files
    
    def generate_code(self, db, table_id: int) -> Tuple[bytes, str]:
        """生成代码并打包为ZIP文件"""
        # 预览代码
        logger.info(f"开始生成代码ZIP文件，表ID: {table_id}")
        code_files = self.preview_code(db, table_id)
        if not code_files:
            logger.error("无法生成代码，表信息不存在或未能生成预览代码")
            raise ValueError("无法生成代码，表信息不存在")
        
        # 获取表信息
        table_obj = gen_table.get(db, table_id)
        logger.info(f"获取到表信息: {table_obj.table_name}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        logger.info(f"创建临时目录: {temp_dir}")
        
        try:
            # 记录已成功写入的文件
            written_files = []
            
            # 写入文件
            for code_file in code_files:
                try:
                    # 处理路径分隔符
                    file_path = os.path.join(temp_dir, code_file.file_path.replace('/', os.path.sep))
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # 写入文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code_file.file_content)
                        
                    written_files.append(file_path)
                    logger.info(f"成功写入文件: {file_path}")
                except Exception as e:
                    logger.error(f"写入文件失败: {code_file.file_path}, 错误: {str(e)}", exc_info=True)
            
            # 创建ZIP文件
            zip_filename = f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
            zip_filepath = os.path.join(temp_dir, zip_filename)
            logger.info(f"开始创建ZIP文件: {zip_filepath}")
            
            try:
                with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    file_count = 0
                    for file_path in written_files:
                        if os.path.isfile(file_path) and os.path.basename(file_path) != zip_filename:
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
                            file_count += 1
                            logger.info(f"添加文件到ZIP: {arcname}")
                    
                    logger.info(f"ZIP文件创建完成，包含 {file_count} 个文件")
                
                # 验证ZIP文件是否有效
                with zipfile.ZipFile(zip_filepath, 'r') as zipf:
                    # 测试ZIP文件的完整性
                    test_result = zipf.testzip()
                    if test_result is not None:
                        logger.error(f"ZIP文件损坏，首个错误文件: {test_result}")
                        raise ValueError(f"生成的ZIP文件已损坏，请联系管理员")
                    
                    logger.info(f"ZIP文件验证通过，包含以下文件: {zipf.namelist()}")
            
                # 读取ZIP文件
                with open(zip_filepath, 'rb') as f:
                    zip_content = f.read()
                
                logger.info(f"成功读取ZIP文件，大小: {len(zip_content)} 字节")
                return zip_content, zip_filename
            except Exception as e:
                logger.error(f"创建或读取ZIP文件失败: {str(e)}", exc_info=True)
                raise ValueError(f"生成ZIP文件失败: {str(e)}")
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"清理临时目录: {temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {str(e)}")
    
    def generate_batch_code(self, db, table_ids: List[int]) -> Tuple[bytes, str]:
        """批量生成代码"""
        if not table_ids:
            logger.error("未选择要生成代码的表")
            raise ValueError("请选择要生成的表")
        
        logger.info(f"开始批量生成代码，表IDs: {table_ids}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        logger.info(f"创建临时目录: {temp_dir}")
        
        try:
            zip_filename = f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
            zip_filepath = os.path.join(temp_dir, zip_filename)
            logger.info(f"开始创建ZIP文件: {zip_filepath}")
            
            try:
                with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    file_count = 0
                    table_count = 0
                    
                    for table_id in table_ids:
                        # 获取表信息
                        table_obj = gen_table.get(db, table_id)
                        if not table_obj:
                            logger.warning(f"表不存在，ID: {table_id}")
                            continue
                        
                        logger.info(f"处理表: {table_obj.table_name}")
                        table_count += 1
                        
                        # 生成表的代码
                        code_files = self.preview_code(db, table_id)
                        if not code_files:
                            logger.warning(f"表 {table_obj.table_name} 没有生成任何代码文件")
                            continue
                        
                        # 表目录名
                        table_dir = table_obj.table_name
                        
                        # 写入ZIP文件
                        for code_file in code_files:
                            try:
                                # 文件内容
                                content = code_file.file_content.encode('utf-8')
                                
                                # ZIP文件中的路径
                                arcname = f"{table_dir}/{code_file.file_path}"
                                
                                # 添加到ZIP
                                zipf.writestr(arcname, content)
                                file_count += 1
                                logger.info(f"添加文件到ZIP: {arcname}")
                            except Exception as e:
                                logger.error(f"添加文件到ZIP失败: {code_file.file_path}, 错误: {str(e)}")
                    
                    logger.info(f"ZIP文件创建完成，包含 {table_count} 个表，{file_count} 个文件")
                
                # 验证ZIP文件是否有效
                with zipfile.ZipFile(zip_filepath, 'r') as zipf:
                    # 测试ZIP文件的完整性
                    test_result = zipf.testzip()
                    if test_result is not None:
                        logger.error(f"ZIP文件损坏，首个错误文件: {test_result}")
                        raise ValueError(f"生成的ZIP文件已损坏，请联系管理员")
                    
                    logger.info(f"ZIP文件验证通过，包含以下文件: {zipf.namelist()}")
            
                # 读取ZIP文件
                with open(zip_filepath, 'rb') as f:
                    zip_content = f.read()
                
                logger.info(f"成功读取ZIP文件，大小: {len(zip_content)} 字节")
                return zip_content, zip_filename
            except Exception as e:
                logger.error(f"创建或读取ZIP文件失败: {str(e)}", exc_info=True)
                raise ValueError(f"生成ZIP文件失败: {str(e)}")
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"清理临时目录: {temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {str(e)}")
    
    def _get_template_files(self, tpl_category: str) -> List[str]:
        """获取指定类别的模板文件列表"""
        # 检查模板目录是否存在
        category_dir = os.path.join(self.template_dir, tpl_category)
        if not os.path.exists(category_dir):
            # 创建默认模板
            self._create_default_templates(tpl_category)
        
        # 获取模板文件列表
        template_files = []
        for root, _, files in os.walk(category_dir):
            for file in files:
                if file.endswith('.py.j2') or file.endswith('.vue.j2') or file.endswith('.html.j2') or file.endswith('.js.j2'):
                    rel_path = os.path.relpath(os.path.join(root, file), category_dir)
                    template_files.append(rel_path)
        
        return template_files
    
    def _process_filename(self, template_file: str, context: Dict[str, Any]) -> str:
        """处理文件名中的变量"""
        filename = template_file
        
        # 替换.j2后缀
        if filename.endswith('.j2'):
            filename = filename[:-3]
        
        # 替换变量
        table = context.get('table', {})
        module_name = table.get('module_name', '')
        business_name = table.get('business_name', '')
        class_name = table.get('class_name', '')
        
        # 替换特殊占位符
        replacements = {
            '${moduleName}': module_name,
            '${businessName}': business_name,
            '${className}': class_name
        }
        
        for placeholder, value in replacements.items():
            filename = filename.replace(placeholder, value)
        
        return filename
    
    def _create_default_templates(self, tpl_category: str) -> None:
        """创建默认模板文件"""
        logger.info(f"开始创建默认模板文件，类别: {tpl_category}")
        category_dir = os.path.join(self.template_dir, tpl_category)
        os.makedirs(category_dir, exist_ok=True)
        
        templates = {
            "model.py.j2": '''from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.db.base_class import Base

class {{ table.class_name }}(Base):
    """
    {{ table.table_comment or table.class_name }}
    """
    __tablename__ = "{{ table.table_name }}"
    
    {% for column in columns %}
    {{ column.field_name }} = Column({{ column.python_type | title }}{% if column.column_type %}({{ column.column_type.replace('(', ', ').replace(')', '') }}){% endif %}, {% if column.is_pk == '1' %}primary_key=True, {% endif %}{% if column.is_pk == '1' %}index=True, {% endif %}{% if column.is_increment == '1' %}autoincrement=True, {% endif %}{% if column.is_required == '1' %}nullable=False, {% endif %}comment="{{ column.column_comment }}")
    {% endfor %}
''',
            "schema.py.j2": '''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class {{ table.class_name }}Base(BaseModel):
    """{{ table.table_comment or table.class_name }}基础信息"""
    {% for column in not_pk_columns %}
    {{ column.field_name }}: {% if column.is_required != '1' %}Optional[{% endif %}{{ column.python_type }}{% if column.is_required != '1' %}]{% endif %} = {% if column.is_required != '1' %}None{% else %}Field(..., description="{{ column.column_comment }}"){% endif %}{% if column.is_required != '1' %} = Field(None, description="{{ column.column_comment }}"){% endif %}
    {% endfor %}

class {{ table.class_name }}Create({{ table.class_name }}Base):
    """创建{{ table.table_comment or table.class_name }}"""
    pass

class {{ table.class_name }}Update({{ table.class_name }}Base):
    """更新{{ table.table_comment or table.class_name }}"""
    pass

class {{ table.class_name }}InDB({{ table.class_name }}Base):
    """数据库中的{{ table.table_comment or table.class_name }}"""
    {% for column in pk_columns %}
    {{ column.field_name }}: {{ column.python_type }}
    {% endfor %}
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    class Config:
        orm_mode = True
''',
            "crud.py.j2": '''from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi.encoders import jsonable_encoder

from app.models.{{ table.module_name }}.{{ table.business_name }} import {{ table.class_name }}
from app.schemas.{{ table.module_name }}.{{ table.business_name }} import {{ table.class_name }}Create, {{ table.class_name }}Update

class CRUD{{ table.class_name }}:
    def get(self, db: Session, id: int) -> Optional[{{ table.class_name }}]:
        return db.query({{ table.class_name }}).filter({{ table.class_name }}.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[{{ table.class_name }}]:
        return db.query({{ table.class_name }}).order_by(desc({{ table.class_name }}.create_time)).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: {{ table.class_name }}Create) -> {{ table.class_name }}:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = {{ table.class_name }}(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: {{ table.class_name }}, obj_in: Union[{{ table.class_name }}Update, Dict[str, Any]]) -> {{ table.class_name }}:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> {{ table.class_name }}:
        obj = db.query({{ table.class_name }}).get(id)
        db.delete(obj)
        db.commit()
        return obj

{{ table.business_name }} = CRUD{{ table.class_name }}()
''',
            "api.py.j2": '''from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.{{ table.module_name }}.{{ table.business_name }} import {{ table.class_name }}
from app.schemas.{{ table.module_name }}.{{ table.business_name }} import {{ table.class_name }}Create, {{ table.class_name }}Update, {{ table.class_name }}InDB
from app.crud.{{ table.module_name }}.{{ table.business_name }} import {{ table.business_name }}

router = APIRouter()

@router.get("/", response_model=List[{{ table.class_name }}InDB])
def read_{{ table.business_name }}s(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取{{ table.table_comment or table.class_name }}列表
    """
    {{ table.business_name }}s = {{ table.business_name }}.get_multi(db, skip=skip, limit=limit)
    return {{ table.business_name }}s

@router.post("/", response_model={{ table.class_name }}InDB)
def create_{{ table.business_name }}(
    *,
    db: Session = Depends(deps.get_db),
    {{ table.business_name }}_in: {{ table.class_name }}Create,
) -> Any:
    """
    创建{{ table.table_comment or table.class_name }}
    """
    {{ table.business_name }}_obj = {{ table.business_name }}.create(db, obj_in={{ table.business_name }}_in)
    return {{ table.business_name }}_obj

@router.get("/{id}", response_model={{ table.class_name }}InDB)
def read_{{ table.business_name }}(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    获取指定{{ table.table_comment or table.class_name }}
    """
    {{ table.business_name }}_obj = {{ table.business_name }}.get(db, id=id)
    if not {{ table.business_name }}_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return {{ table.business_name }}_obj

@router.put("/{id}", response_model={{ table.class_name }}InDB)
def update_{{ table.business_name }}(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    {{ table.business_name }}_in: {{ table.class_name }}Update,
) -> Any:
    """
    更新{{ table.table_comment or table.class_name }}
    """
    {{ table.business_name }}_obj = {{ table.business_name }}.get(db, id=id)
    if not {{ table.business_name }}_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    {{ table.business_name }}_obj = {{ table.business_name }}.update(db, db_obj={{ table.business_name }}_obj, obj_in={{ table.business_name }}_in)
    return {{ table.business_name }}_obj

@router.delete("/{id}", response_model={{ table.class_name }}InDB)
def delete_{{ table.business_name }}(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    删除{{ table.table_comment or table.class_name }}
    """
    {{ table.business_name }}_obj = {{ table.business_name }}.get(db, id=id)
    if not {{ table.business_name }}_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    {{ table.business_name }}_obj = {{ table.business_name }}.remove(db, id=id)
    return {{ table.business_name }}_obj
''',
            "vue_api.js.j2": '''import request from '@/request'

// 查询{{ table.table_comment or table.class_name }}列表
export function list{{ table.class_name }}(query) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}/list',
    method: 'get',
    params: query
  })
}

// 查询{{ table.table_comment or table.class_name }}详细
export function get{{ table.class_name }}(id) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}/' + id,
    method: 'get'
  })
}

// 新增{{ table.table_comment or table.class_name }}
export function add{{ table.class_name }}(data) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}',
    method: 'post',
    data: data
  })
}

// 修改{{ table.table_comment or table.class_name }}
export function update{{ table.class_name }}(id, data) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}/' + id,
    method: 'put',
    data: data
  })
}

// 删除{{ table.table_comment or table.class_name }}
export function del{{ table.class_name }}(id) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}/' + id,
    method: 'delete'
  })
}

// 导出{{ table.table_comment or table.class_name }}
export function export{{ table.class_name }}(query) {
  return request({
    url: '/{{ table.module_name }}/{{ table.business_name }}/export',
    method: 'get',
    params: query
  })
}
''',
            "vue_index.vue.j2": '''<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ table.table_comment or table.class_name }}管理</span>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <el-form :model="queryParams" ref="queryForm" :inline="true" v-show="showSearch">
        {% for column in columns %}
        {% if column.is_query == '1' %}
        <el-form-item label="{{ column.column_comment }}" prop="{{ column.field_name }}">
          <el-input
            v-model="queryParams.{{ column.field_name }}"
            placeholder="请输入{{ column.column_comment }}"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        {% endif %}
        {% endfor %}
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 操作工具栏 -->
      <el-row :gutter="10" class="mb8">
        <el-col :span="1.5">
          <el-button
            type="primary"
            plain
            icon="el-icon-plus"
            @click="handleAdd"
            v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:add']"
          >新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            icon="el-icon-edit"
            :disabled="single"
            @click="handleUpdate"
            v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:edit']"
          >修改</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            icon="el-icon-delete"
            :disabled="multiple"
            @click="handleDelete"
            v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:remove']"
          >删除</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="warning"
            plain
            icon="el-icon-download"
            @click="handleExport"
            v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:export']"
          >导出</el-button>
        </el-col>
        <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="dataList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="序号" type="index" width="50" align="center" />
        {% for column in columns %}
        {% if column.is_list == '1' %}
        <el-table-column label="{{ column.column_comment }}" prop="{{ column.field_name }}" {% if column.list_width %}width="{{ column.list_width }}"{% endif %} {% if column.dict_type %}:formatter="dict{{ column.dict_type }}Format"{% endif %} />
        {% endif %}
        {% endfor %}
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:edit']"
            >修改</el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['{{ table.module_name }}:{{ table.business_name }}:remove']"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页组件 -->
      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="getList"
      />

      <!-- 添加或修改对话框 -->
      <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
        <el-form ref="form" :model="form" :rules="rules" label-width="100px">
          {% for column in columns %}
          {% if column.is_edit == '1' %}
          <el-form-item label="{{ column.column_comment }}" prop="{{ column.field_name }}">
            {% if column.html_type == 'input' %}
            <el-input v-model="form.{{ column.field_name }}" placeholder="请输入{{ column.column_comment }}" />
            {% elif column.html_type == 'textarea' %}
            <el-input v-model="form.{{ column.field_name }}" type="textarea" placeholder="请输入{{ column.column_comment }}" />
            {% elif column.html_type == 'select' and column.dict_type %}
            <el-select v-model="form.{{ column.field_name }}" placeholder="请选择{{ column.column_comment }}">
              <el-option
                v-for="dict in dict.type.{{ column.dict_type }}"
                :key="dict.value"
                :label="dict.label"
                :value="dict.value"
              ></el-option>
            </el-select>
            {% elif column.html_type == 'radio' and column.dict_type %}
            <el-radio-group v-model="form.{{ column.field_name }}">
              <el-radio
                v-for="dict in dict.type.{{ column.dict_type }}"
                :key="dict.value"
                :label="dict.value"
              >{{dict.label}}</el-radio>
            </el-radio-group>
            {% elif column.html_type == 'datetime' %}
            <el-date-picker
              v-model="form.{{ column.field_name }}"
              type="datetime"
              placeholder="选择日期时间"
            />
            {% endif %}
          </el-form-item>
          {% endif %}
          {% endfor %}
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button type="primary" @click="submitForm">确 定</el-button>
            <el-button @click="cancel">取 消</el-button>
          </div>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import { list{{ table.class_name }}, get{{ table.class_name }}, add{{ table.class_name }}, update{{ table.class_name }}, del{{ table.class_name }} } from "@/api/{{ table.module_name }}/{{ table.business_name }}";

export default {
  name: "{{ table.class_name }}",
  {% if dict_types and dict_types|length > 0 %}
  dicts: [{% for dict_type in dict_types %}'{{ dict_type }}'{% if not loop.last %}, {% endif %}{% endfor %}],
  {% endif %}
  data() {
    return {
      // 遮罩层
      loading: false,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // {{ table.table_comment or table.class_name }}表格数据
      dataList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        {% for column in columns %}
        {% if column.is_query == '1' %}
        {{ column.field_name }}: null,
        {% endif %}
        {% endfor %}
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        {% for column in columns %}
        {% if column.is_required == '1' and column.is_edit == '1' %}
        {{ column.field_name }}: [
          { required: true, message: "{{ column.column_comment }}不能为空", trigger: "blur" }
        ],
        {% endif %}
        {% endfor %}
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询{{ table.table_comment or table.class_name }}列表 */
    getList() {
      this.loading = true;
      list{{ table.class_name }}(this.queryParams).then(response => {
        this.dataList = response.data.items || response.data;
        this.total = response.data.total || this.dataList.length;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        {% for column in columns %}
        {% if column.is_edit == '1' %}
        {{ column.field_name }}: null,
        {% endif %}
        {% endfor %}
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.id)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加{{ table.table_comment or table.class_name }}";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids[0]
      get{{ table.class_name }}(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改{{ table.table_comment or table.class_name }}";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.id != null) {
            update{{ table.class_name }}(this.form.id, this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            add{{ table.class_name }}(this.form).then(response => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const ids = row.id || this.ids;
      this.$modal.confirm('是否确认删除编号为"' + ids + '"的数据项？').then(function() {
        return del{{ table.class_name }}(ids);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('{{ table.module_name }}/{{ table.business_name }}/export', {
        ...this.queryParams
      }, `{{ table.business_name }}_${new Date().getTime()}.xlsx`)
    }
  }
};
</script>
''',
        }
        
        created_count = 0
        for template_name, template_content in templates.items():
            try:
                template_path = os.path.join(category_dir, template_name)
                logger.info(f"创建模板文件: {template_path}")
                
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                # 验证文件是否成功创建
                if os.path.exists(template_path):
                    created_count += 1
                    logger.info(f"模板文件创建成功: {template_path}")
                else:
                    logger.warning(f"模板文件未能成功创建: {template_path}")
            except Exception as e:
                logger.error(f"创建模板文件 {template_name} 失败: {str(e)}", exc_info=True)
        
        logger.info(f"创建默认模板文件完成，成功创建: {created_count}/{len(templates)}")


# 实例化
gen_service = GenService()