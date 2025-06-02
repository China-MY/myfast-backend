from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SysRole(Base):
    """系统角色表"""
    __tablename__ = "sys_role"
    
    role_id = Column(Integer, primary_key=True, autoincrement=True, comment="角色ID")
    role_name = Column(String(30), nullable=False, comment="角色名称")
    role_key = Column(String(100), nullable=False, comment="角色权限字符串")
    role_sort = Column(Integer, nullable=False, comment="显示顺序")
    data_scope = Column(String(1), default="1", comment="数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）")
    status = Column(String(1), nullable=False, comment="角色状态（0正常 1停用）")
    del_flag = Column(String(1), default="0", comment="删除标志（0代表存在 1代表删除）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    remark = Column(String(500), comment="备注")

    # 关联关系
    users = relationship("SysUser", secondary="sys_user_role", back_populates="roles")
    menus = relationship("SysMenu", secondary="sys_role_menu", back_populates="roles")
    depts = relationship("SysDept", secondary="sys_role_dept", back_populates="roles") 