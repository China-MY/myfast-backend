"""系统常量定义"""

# 用户类型
class UserType:
    """用户类型常量"""
    # 系统用户
    SYSTEM = "00"
    # 普通用户
    NORMAL = "01"

# 用户状态
class UserStatus:
    """用户状态常量"""
    # 正常
    NORMAL = "0"
    # 停用
    DISABLE = "1"

# 删除标志
class DelFlag:
    """删除标志常量"""
    # 正常
    NORMAL = "0"
    # 删除
    DELETE = "2"

# 菜单类型
class MenuType:
    """菜单类型常量"""
    # 目录
    DIRECTORY = "M"
    # 菜单
    MENU = "C"
    # 按钮
    BUTTON = "F"

# 性别
class Gender:
    """性别常量"""
    # 男
    MALE = "0"
    # 女
    FEMALE = "1"
    # 未知
    UNKNOWN = "2"

# 是否（Y是 N否）
class YesNo:
    """是否常量"""
    # 是
    YES = "Y"
    # 否
    NO = "N"

# 状态（0正常 1停用）
class Status:
    """状态常量"""
    # 正常
    NORMAL = "0"
    # 停用
    DISABLE = "1" 