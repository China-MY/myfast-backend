from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.relation import SysRoleMenu


class SysMenu(Base):
    """系统菜单表"""
    __tablename__ = "sys_menu"

    menu_id = Column(Integer, primary_key=True, autoincrement=True, comment="菜单ID")
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    parent_id = Column(Integer, default=0, comment="父菜单ID")
    order_num = Column(Integer, default=0, comment="显示顺序")
    path = Column(String(200), default="", comment="路由地址")
    component = Column(String(255), nullable=True, comment="组件路径")
    query = Column(String(255), nullable=True, comment="路由参数")
    is_frame = Column(Integer, default=1, comment="是否为外链（0是 1否）")
    is_cache = Column(Integer, default=0, comment="是否缓存（0缓存 1不缓存）")
    menu_type = Column(String(1), default="", comment="菜单类型（M目录 C菜单 F按钮）")
    visible = Column(String(1), default="0", comment="菜单状态（0显示 1隐藏）")
    status = Column(String(1), default="0", comment="菜单状态（0正常 1停用）")
    perms = Column(String(100), nullable=True, comment="权限标识")
    icon = Column(String(100), default="#", comment="菜单图标")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default="", comment="备注")

    # 关系
    roles = relationship("SysRole", secondary=SysRoleMenu, back_populates="menus") 