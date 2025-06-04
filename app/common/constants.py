"""
系统常量定义
"""
from enum import Enum


class StatusEnum(str, Enum):
    """状态枚举"""
    NORMAL = "0"  # 正常
    DISABLE = "1"  # 停用


class UserStatusEnum(str, Enum):
    """用户状态枚举"""
    NORMAL = "0"  # 正常
    DISABLE = "1"  # 停用


class DeleteFlagEnum(str, Enum):
    """删除标志枚举"""
    NORMAL = "0"  # 正常
    DELETED = "1"  # 已删除


class MenuTypeEnum(str, Enum):
    """菜单类型枚举"""
    DIRECTORY = "M"  # 目录
    MENU = "C"  # 菜单
    BUTTON = "F"  # 按钮


class VisibleEnum(str, Enum):
    """显示状态枚举"""
    SHOW = "0"  # 显示
    HIDE = "1"  # 隐藏


class YesNoEnum(str, Enum):
    """是/否枚举"""
    YES = "Y"  # 是
    NO = "N"  # 否


class SexEnum(str, Enum):
    """性别枚举"""
    MALE = "0"  # 男
    FEMALE = "1"  # 女
    UNKNOWN = "2"  # 未知


class UserTypeEnum(str, Enum):
    """用户类型枚举"""
    SYSTEM_USER = "00"  # 系统用户


class DataScopeEnum(str, Enum):
    """数据范围枚举"""
    ALL = "1"  # 全部数据权限
    CUSTOM = "2"  # 自定义数据权限
    DEPT = "3"  # 本部门数据权限
    DEPT_AND_CHILD = "4"  # 本部门及以下数据权限 