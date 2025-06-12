-- 创建代码生成业务表
CREATE TABLE IF NOT EXISTS `gen_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '编号',
  `table_name` varchar(200) NOT NULL COMMENT '表名称',
  `table_comment` varchar(500) DEFAULT NULL COMMENT '表描述',
  `class_name` varchar(100) DEFAULT NULL COMMENT '类名称',
  `package_name` varchar(100) DEFAULT 'app.models' COMMENT '生成包路径',
  `module_name` varchar(30) DEFAULT NULL COMMENT '生成模块名',
  `business_name` varchar(30) DEFAULT NULL COMMENT '生成业务名',
  `function_name` varchar(50) DEFAULT NULL COMMENT '生成功能名',
  `function_author` varchar(50) DEFAULT NULL COMMENT '生成功能作者',
  `tpl_category` varchar(20) DEFAULT 'crud' COMMENT '使用的模板（crud单表操作 tree树表操作）',
  `options` varchar(1000) DEFAULT NULL COMMENT '其它生成选项',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码生成业务表';

-- 创建代码生成业务表字段
CREATE TABLE IF NOT EXISTS `gen_table_column` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '编号',
  `table_id` int(11) NOT NULL COMMENT '归属表编号',
  `column_name` varchar(200) NOT NULL COMMENT '列名称',
  `column_comment` varchar(500) DEFAULT NULL COMMENT '列描述',
  `column_type` varchar(100) DEFAULT NULL COMMENT '列类型',
  `python_type` varchar(500) DEFAULT NULL COMMENT 'Python类型',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名',
  `is_pk` char(1) DEFAULT '0' COMMENT '是否主键（1是）',
  `is_increment` char(1) DEFAULT '0' COMMENT '是否自增（1是）',
  `is_required` char(1) DEFAULT '0' COMMENT '是否必填（1是）',
  `is_insert` char(1) DEFAULT '0' COMMENT '是否为插入字段（1是）',
  `is_edit` char(1) DEFAULT '0' COMMENT '是否编辑字段（1是）',
  `is_list` char(1) DEFAULT '0' COMMENT '是否列表字段（1是）',
  `is_query` char(1) DEFAULT '0' COMMENT '是否查询字段（1是）',
  `query_type` varchar(200) DEFAULT 'EQ' COMMENT '查询方式（等于、不等于、大于、小于、范围）',
  `html_type` varchar(200) DEFAULT NULL COMMENT '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）',
  `dict_type` varchar(200) DEFAULT NULL COMMENT '字典类型',
  `sort` int(11) DEFAULT NULL COMMENT '排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_table_id` (`table_id`),
  CONSTRAINT `fk_gen_table_column_table_id` FOREIGN KEY (`table_id`) REFERENCES `gen_table` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码生成业务表字段'; 