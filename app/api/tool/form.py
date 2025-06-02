from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
import json
import os

from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.common.response import success, error
from app.core.config import settings

router = APIRouter()


@router.get("/designer", summary="获取表单设计器组件")
async def get_form_designer(
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取表单设计器组件
    """
    try:
        # 表单设计器组件列表
        designer_components = [
            {
                "component_id": 1,
                "component_type": "input",
                "component_name": "单行文本",
                "icon": "form",
                "props": {
                    "type": "text",
                    "placeholder": "请输入",
                    "maxlength": 50,
                    "showWordLimit": True
                }
            },
            {
                "component_id": 2,
                "component_type": "textarea",
                "component_name": "多行文本",
                "icon": "document",
                "props": {
                    "placeholder": "请输入",
                    "maxlength": 200,
                    "showWordLimit": True,
                    "rows": 4
                }
            },
            {
                "component_id": 3,
                "component_type": "number",
                "component_name": "计数器",
                "icon": "plus",
                "props": {
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "controls": True
                }
            },
            {
                "component_id": 4,
                "component_type": "radio",
                "component_name": "单选框",
                "icon": "check",
                "props": {
                    "options": [
                        {"label": "选项1", "value": "1"},
                        {"label": "选项2", "value": "2"}
                    ],
                    "button": False
                }
            },
            {
                "component_id": 5,
                "component_type": "checkbox",
                "component_name": "多选框",
                "icon": "check-square",
                "props": {
                    "options": [
                        {"label": "选项1", "value": "1"},
                        {"label": "选项2", "value": "2"}
                    ],
                    "button": False
                }
            },
            {
                "component_id": 6,
                "component_type": "select",
                "component_name": "下拉选择",
                "icon": "arrow-down",
                "props": {
                    "options": [
                        {"label": "选项1", "value": "1"},
                        {"label": "选项2", "value": "2"}
                    ],
                    "clearable": True,
                    "multiple": False
                }
            },
            {
                "component_id": 7,
                "component_type": "switch",
                "component_name": "开关",
                "icon": "switch",
                "props": {
                    "activeText": "是",
                    "inactiveText": "否"
                }
            },
            {
                "component_id": 8,
                "component_type": "slider",
                "component_name": "滑块",
                "icon": "minus",
                "props": {
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "showInput": True
                }
            },
            {
                "component_id": 9,
                "component_type": "time",
                "component_name": "时间选择器",
                "icon": "time",
                "props": {
                    "placeholder": "请选择时间",
                    "format": "HH:mm:ss",
                    "clearable": True
                }
            },
            {
                "component_id": 10,
                "component_type": "date",
                "component_name": "日期选择器",
                "icon": "date",
                "props": {
                    "placeholder": "请选择日期",
                    "format": "YYYY-MM-DD",
                    "clearable": True,
                    "type": "date"
                }
            },
            {
                "component_id": 11,
                "component_type": "datetime",
                "component_name": "日期时间选择器",
                "icon": "calendar",
                "props": {
                    "placeholder": "请选择日期时间",
                    "format": "YYYY-MM-DD HH:mm:ss",
                    "clearable": True,
                    "type": "datetime"
                }
            },
            {
                "component_id": 12,
                "component_type": "rate",
                "component_name": "评分",
                "icon": "star",
                "props": {
                    "max": 5,
                    "allowHalf": False,
                    "showText": False
                }
            },
            {
                "component_id": 13,
                "component_type": "color",
                "component_name": "颜色选择器",
                "icon": "brush",
                "props": {
                    "showAlpha": False
                }
            },
            {
                "component_id": 14,
                "component_type": "upload",
                "component_name": "上传组件",
                "icon": "upload",
                "props": {
                    "action": "/api/v1/system/file/upload",
                    "multiple": False,
                    "listType": "text"
                }
            }
        ]
        
        return success(data=designer_components)
    except Exception as e:
        return error(msg=str(e))


@router.get("/template", summary="获取表单模板")
async def get_form_template(
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取表单模板列表
    """
    try:
        # 表单模板列表
        form_templates = [
            {
                "template_id": 1,
                "template_name": "基础表单",
                "template_desc": "基础表单模板，包含常用的表单元素",
                "template_thumb": "/static/form/basic_form.png",
                "template_json": json.dumps({
                    "formRef": "elForm",
                    "formModel": "formData",
                    "size": "medium",
                    "labelPosition": "right",
                    "labelWidth": 100,
                    "formRules": "rules",
                    "gutter": 15,
                    "disabled": False,
                    "span": 24,
                    "formBtns": True,
                    "fields": [
                        {
                            "field": "name",
                            "label": "姓名",
                            "component": "input",
                            "required": True,
                            "props": {
                                "placeholder": "请输入姓名"
                            }
                        },
                        {
                            "field": "age",
                            "label": "年龄",
                            "component": "number",
                            "required": True,
                            "props": {
                                "min": 0,
                                "max": 120
                            }
                        },
                        {
                            "field": "gender",
                            "label": "性别",
                            "component": "radio",
                            "required": True,
                            "props": {
                                "options": [
                                    {"label": "男", "value": "male"},
                                    {"label": "女", "value": "female"}
                                ]
                            }
                        },
                        {
                            "field": "birth",
                            "label": "出生日期",
                            "component": "date",
                            "required": True,
                            "props": {
                                "placeholder": "请选择出生日期"
                            }
                        },
                        {
                            "field": "desc",
                            "label": "个人简介",
                            "component": "textarea",
                            "required": False,
                            "props": {
                                "placeholder": "请输入个人简介",
                                "rows": 4
                            }
                        }
                    ]
                })
            },
            {
                "template_id": 2,
                "template_name": "高级表单",
                "template_desc": "高级表单模板，包含复杂的表单元素和布局",
                "template_thumb": "/static/form/advanced_form.png",
                "template_json": json.dumps({
                    "formRef": "elForm",
                    "formModel": "formData",
                    "size": "medium",
                    "labelPosition": "right",
                    "labelWidth": 120,
                    "formRules": "rules",
                    "gutter": 15,
                    "disabled": False,
                    "span": 24,
                    "formBtns": True,
                    "fields": [
                        {
                            "field": "basicInfo",
                            "label": "基本信息",
                            "component": "card",
                            "children": [
                                {
                                    "field": "name",
                                    "label": "姓名",
                                    "component": "input",
                                    "required": True,
                                    "props": {
                                        "placeholder": "请输入姓名"
                                    }
                                },
                                {
                                    "field": "idNumber",
                                    "label": "身份证号",
                                    "component": "input",
                                    "required": True,
                                    "props": {
                                        "placeholder": "请输入身份证号"
                                    }
                                }
                            ]
                        },
                        {
                            "field": "contactInfo",
                            "label": "联系方式",
                            "component": "card",
                            "children": [
                                {
                                    "field": "phone",
                                    "label": "手机号码",
                                    "component": "input",
                                    "required": True,
                                    "props": {
                                        "placeholder": "请输入手机号码"
                                    }
                                },
                                {
                                    "field": "email",
                                    "label": "电子邮箱",
                                    "component": "input",
                                    "required": False,
                                    "props": {
                                        "placeholder": "请输入电子邮箱"
                                    }
                                },
                                {
                                    "field": "address",
                                    "label": "联系地址",
                                    "component": "textarea",
                                    "required": False,
                                    "props": {
                                        "placeholder": "请输入联系地址",
                                        "rows": 3
                                    }
                                }
                            ]
                        },
                        {
                            "field": "otherInfo",
                            "label": "其他信息",
                            "component": "card",
                            "children": [
                                {
                                    "field": "hobby",
                                    "label": "兴趣爱好",
                                    "component": "checkbox",
                                    "required": False,
                                    "props": {
                                        "options": [
                                            {"label": "阅读", "value": "reading"},
                                            {"label": "音乐", "value": "music"},
                                            {"label": "运动", "value": "sports"},
                                            {"label": "旅游", "value": "travel"}
                                        ]
                                    }
                                },
                                {
                                    "field": "avatar",
                                    "label": "个人头像",
                                    "component": "upload",
                                    "required": False,
                                    "props": {
                                        "action": "/api/v1/system/file/upload",
                                        "listType": "picture-card"
                                    }
                                }
                            ]
                        }
                    ]
                })
            }
        ]
        
        return success(data=form_templates)
    except Exception as e:
        return error(msg=str(e))


@router.post("/save", summary="保存表单配置")
async def save_form_config(
    form_config: Dict[str, Any],
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    保存表单配置
    """
    try:
        # 这里只是模拟保存，实际应用中需要保存到数据库
        return success(msg="保存成功", data={"id": 1})
    except Exception as e:
        return error(msg=str(e))


@router.get("/render/{form_id}", summary="渲染表单")
async def render_form(
    form_id: int,
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    根据表单ID渲染表单
    """
    try:
        # 模拟从数据库获取表单配置
        form_config = {
            "formRef": "elForm",
            "formModel": "formData",
            "size": "medium",
            "labelPosition": "right",
            "labelWidth": 100,
            "formRules": "rules",
            "gutter": 15,
            "disabled": False,
            "span": 24,
            "formBtns": True,
            "fields": [
                {
                    "field": "name",
                    "label": "姓名",
                    "component": "input",
                    "required": True,
                    "props": {
                        "placeholder": "请输入姓名"
                    }
                },
                {
                    "field": "age",
                    "label": "年龄",
                    "component": "number",
                    "required": True,
                    "props": {
                        "min": 0,
                        "max": 120
                    }
                }
            ]
        }
        
        return success(data=form_config)
    except Exception as e:
        return error(msg=str(e)) 