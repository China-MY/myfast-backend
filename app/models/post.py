from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


# 用户与岗位关联表
user_post = Table(
    "sys_user_post",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True),
    Column("post_id", Integer, ForeignKey("sys_post.post_id"), primary_key=True)
)


class Post(Base):
    __tablename__ = "sys_post"

    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_code = Column(String(64), nullable=False)
    post_name = Column(String(50), nullable=False)
    post_sort = Column(Integer, nullable=False)
    status = Column(String(1), nullable=False)
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), nullable=True)

    # 关系定义
    users = relationship("User", secondary=user_post, back_populates="posts")

    def __repr__(self):
        return f"<Post {self.post_name}>" 