from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base


# 用户与岗位关联表
SysUserPost = Table(
    "sys_user_post",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.user_id"), primary_key=True, comment="用户ID"),
    Column("post_id", Integer, ForeignKey("sys_post.post_id"), primary_key=True, comment="岗位ID"),
) 