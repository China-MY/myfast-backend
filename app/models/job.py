from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

from app.db.base_class import Base


class SysJob(Base):
    """定时任务调度表"""
    __tablename__ = "sys_job"
    
    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="任务ID")
    job_name = Column(String(64), default="", comment="任务名称")
    job_group = Column(String(64), default="default", comment="任务组名")
    invoke_target = Column(String(500), default="", comment="调用目标字符串")
    job_params = Column(Text, nullable=True, comment="任务参数")
    cron_expression = Column(String(255), default="", comment="cron执行表达式")
    misfire_policy = Column(String(1), default="3", comment="计划执行策略（1立即执行 2执行一次 3放弃执行）")
    concurrent = Column(String(1), default="1", comment="是否并发执行（0允许 1禁止）")
    status = Column(String(1), default="0", comment="状态（0正常 1暂停）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注信息")


class SysJobLog(Base):
    """定时任务调度日志表"""
    __tablename__ = "sys_job_log"
    
    job_log_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="任务日志ID")
    job_id = Column(Integer, nullable=True, comment="任务ID")
    job_name = Column(String(64), default="", comment="任务名称")
    job_group = Column(String(64), default="", comment="任务组名")
    invoke_target = Column(String(500), default="", comment="调用目标字符串")
    job_message = Column(String(500), nullable=True, comment="日志信息")
    status = Column(String(1), default="0", comment="执行状态（0正常 1失败）")
    exception_info = Column(Text, nullable=True, comment="异常信息")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间") 