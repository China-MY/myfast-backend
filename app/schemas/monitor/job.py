from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """任务调度基础Schema"""
    job_name: str = Field(..., description="任务名称")
    job_group: str = Field(..., description="任务组名")
    invoke_target: str = Field(..., description="调用目标字符串")
    cron_expression: Optional[str] = Field(None, description="cron执行表达式")
    misfire_policy: Optional[str] = Field("3", description="计划执行策略（1立即执行 2执行一次 3放弃执行）")
    concurrent: Optional[str] = Field("1", description="是否并发执行（0允许 1禁止）")
    status: Optional[str] = Field("0", description="状态（0正常 1暂停）")
    remark: Optional[str] = Field(None, description="备注信息")


class JobCreate(JobBase):
    """创建任务的Schema"""
    # 移除job_params字段，因为数据库中不存在该字段
    # job_params: Optional[str] = Field(None, description="任务参数")
    pass


class JobUpdate(JobBase):
    """更新任务的Schema"""
    job_id: int = Field(..., description="任务ID")
    job_name: Optional[str] = Field(None, description="任务名称")
    job_group: Optional[str] = Field(None, description="任务组名")
    invoke_target: Optional[str] = Field(None, description="调用目标字符串")
    # 移除job_params字段
    # job_params: Optional[str] = Field(None, description="任务参数")


class JobInDBBase(JobBase):
    """数据库中任务的Schema"""
    job_id: int
    # 移除job_params字段
    # job_params: Optional[str] = None
    create_by: str
    create_time: datetime
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class JobOut(JobInDBBase):
    """返回的任务Schema"""
    pass


class JobPagination(BaseModel):
    """任务分页Schema"""
    rows: List[JobOut]
    total: int


class JobLogBase(BaseModel):
    """任务日志基础Schema"""
    job_name: str = Field(..., description="任务名称")
    job_group: str = Field(..., description="任务组名")
    invoke_target: str = Field(..., description="调用目标字符串")
    job_message: Optional[str] = Field(None, description="日志信息")
    status: str = Field("0", description="执行状态（0正常 1失败）")
    exception_info: Optional[str] = Field(None, description="异常信息")


class JobLogCreate(JobLogBase):
    """创建任务日志的Schema"""
    # 以下字段在数据库表中不存在，移除
    # job_id: Optional[int] = Field(None, description="任务ID")
    # start_time: Optional[datetime] = Field(None, description="开始时间")
    # end_time: Optional[datetime] = Field(None, description="结束时间")
    pass


class JobLogInDBBase(JobLogBase):
    """数据库中任务日志的Schema"""
    job_log_id: int
    # 以下字段在数据库表中不存在，移除
    # job_id: Optional[int] = None
    # start_time: Optional[datetime] = None
    # end_time: Optional[datetime] = None
    create_time: datetime
    
    model_config = {"from_attributes": True}


class JobLogOut(JobLogInDBBase):
    """返回的任务日志Schema"""
    # 由于start_time和end_time不存在，无法计算运行时间
    # run_time: Optional[float] = None
    pass


class JobLogPagination(BaseModel):
    """任务日志分页Schema"""
    rows: List[JobLogOut]
    total: int 