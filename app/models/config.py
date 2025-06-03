from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.session import Base


class Config(Base):
    __tablename__ = "sys_config"

    config_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_name = Column(String(100), default="")
    config_key = Column(String(100), default="", index=True)
    config_value = Column(String(500), default="")
    config_type = Column(String(1), default="N")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now)
    remark = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Config {self.config_name}>" 