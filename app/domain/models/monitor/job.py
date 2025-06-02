from sqlalchemy import Column, Integer, String, DateTime, Text, func

from app.db.database import Base


class SysJob(Base):
    """定时任务调度表"""
    __tablename__ = "sys_job"
    
    job_id = Column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    job_name = Column(String(64), nullable=False, comment="任务名称")
    job_group = Column(String(64), default="DEFAULT", comment="任务组名")
    job_params = Column(Text, comment="任务参数")
    cron_expression = Column(String(255), nullable=False, comment="cron执行表达式")
    misfire_policy = Column(String(20), default="3", comment="计划执行错误策略（1立即执行 2执行一次 3放弃执行）")
    concurrent = Column(String(1), default="1", comment="是否并发执行（0允许 1禁止）")
    status = Column(String(1), default="0", comment="状态（0正常 1暂停）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=func.now(), comment="更新时间")
    remark = Column(String(500), default="", comment="备注信息")


class SysJobLog(Base):
    """定时任务调度日志表"""
    __tablename__ = "sys_job_log"
    
    job_log_id = Column(Integer, primary_key=True, autoincrement=True, comment="任务日志ID")
    job_id = Column(Integer, nullable=False, comment="任务ID")
    job_name = Column(String(64), nullable=False, comment="任务名称")
    job_group = Column(String(64), nullable=False, comment="任务组名")
    job_params = Column(Text, comment="任务参数")
    job_message = Column(Text, comment="日志信息")
    status = Column(String(1), default="0", comment="执行状态（0正常 1失败）")
    exception_info = Column(Text, comment="异常信息")
    create_time = Column(DateTime, default=func.now(), comment="创建时间") 