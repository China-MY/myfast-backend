from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.relation import SysUserPost


class SysPost(Base):
    """岗位表"""
    __tablename__ = "sys_post"

    post_id = Column(Integer, primary_key=True, autoincrement=True, comment="岗位ID")
    post_code = Column(String(64), nullable=False, comment="岗位编码")
    post_name = Column(String(50), nullable=False, comment="岗位名称")
    post_sort = Column(Integer, nullable=False, comment="显示顺序")
    status = Column(String(1), nullable=False, comment="状态（0正常 1停用）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")

    # 关系
    users = relationship("SysUser", secondary=SysUserPost, back_populates="posts") 