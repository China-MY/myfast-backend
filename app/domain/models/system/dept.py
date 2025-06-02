from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SysDept(Base):
    """系统部门表"""
    __tablename__ = "sys_dept"
    
    dept_id = Column(Integer, primary_key=True, autoincrement=True, comment="部门id")
    parent_id = Column(Integer, default=0, comment="父部门id")
    ancestors = Column(String(50), default="", comment="祖级列表")
    dept_name = Column(String(30), default="", comment="部门名称")
    order_num = Column(Integer, default=0, comment="显示顺序")
    leader = Column(String(20), comment="负责人")
    phone = Column(String(11), comment="联系电话")
    email = Column(String(50), comment="邮箱")
    status = Column(String(1), default="0", comment="部门状态（0正常 1停用）")
    del_flag = Column(String(1), default="0", comment="删除标志（0代表存在 1代表删除）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    users = relationship("SysUser", back_populates="dept")
    roles = relationship("SysRole", secondary="sys_role_dept", back_populates="depts") 