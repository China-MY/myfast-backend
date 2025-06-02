from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class JobBase(BaseModel):
    """定时任务基础信息"""
    job_name: str = Field(..., description="任务名称")
    job_group: str = Field("DEFAULT", description="任务组名")
    job_params: Optional[str] = Field(None, description="任务参数")
    cron_expression: str = Field(..., description="cron执行表达式")
    misfire_policy: str = Field("3", description="计划执行错误策略（1立即执行 2执行一次 3放弃执行）")
    concurrent: str = Field("1", description="是否并发执行（0允许 1禁止）")
    status: str = Field("0", description="状态（0正常 1暂停）")
    remark: Optional[str] = Field(None, description="备注")


class JobCreate(JobBase):
    """创建定时任务"""
    pass


class JobUpdate(JobBase):
    """更新定时任务"""
    job_id: int = Field(..., description="任务ID")


class JobInfo(JobBase):
    """定时任务详细信息"""
    job_id: int = Field(..., description="任务ID")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class JobQuery(BaseModel):
    """定时任务查询参数"""
    job_name: Optional[str] = Field(None, description="任务名称")
    job_group: Optional[str] = Field(None, description="任务组名")
    status: Optional[str] = Field(None, description="状态（0正常 1暂停）")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100)


class JobLogQuery(BaseModel):
    """定时任务日志查询参数"""
    job_name: Optional[str] = Field(None, description="任务名称")
    job_group: Optional[str] = Field(None, description="任务组名")
    status: Optional[str] = Field(None, description="执行状态（0正常 1失败）")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100) 