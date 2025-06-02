from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.monitor.job import SysJob, SysJobLog
from app.domain.schemas.monitor.job import JobCreate, JobUpdate, JobInfo, JobQuery, JobLogQuery
from app.common.exception import NotFound


def get_job(db: Session, job_id: int) -> Optional[SysJob]:
    """
    根据任务ID获取定时任务信息
    """
    return db.query(SysJob).filter(SysJob.job_id == job_id).first()


def get_job_by_name_and_group(db: Session, job_name: str, job_group: str) -> Optional[SysJob]:
    """
    根据任务名称和组名获取定时任务信息
    """
    return db.query(SysJob).filter(
        SysJob.job_name == job_name,
        SysJob.job_group == job_group
    ).first()


def get_jobs(
    db: Session, 
    params: JobQuery
) -> Tuple[List[SysJob], int]:
    """
    获取定时任务列表（分页查询）
    """
    query = db.query(SysJob)
    
    # 构建查询条件
    if params.job_name:
        query = query.filter(SysJob.job_name.like(f"%{params.job_name}%"))
    if params.job_group:
        query = query.filter(SysJob.job_group == params.job_group)
    if params.status:
        query = query.filter(SysJob.status == params.status)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysJob.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    jobs = query.order_by(SysJob.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return jobs, total


def create_job(
    db: Session, 
    job_data: JobCreate
) -> SysJob:
    """
    创建定时任务
    """
    # 检查任务名称和组名是否已存在
    if get_job_by_name_and_group(db, job_data.job_name, job_data.job_group):
        raise ValueError(f"任务名称 {job_data.job_name} 在组 {job_data.job_group} 中已存在")
    
    # 创建定时任务对象
    db_job = SysJob(
        job_name=job_data.job_name,
        job_group=job_data.job_group,
        job_params=job_data.job_params,
        cron_expression=job_data.cron_expression,
        misfire_policy=job_data.misfire_policy,
        concurrent=job_data.concurrent,
        status=job_data.status,
        remark=job_data.remark
    )
    
    # 保存定时任务信息
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


def update_job(
    db: Session, 
    job_id: int, 
    job_data: JobUpdate
) -> Optional[SysJob]:
    """
    更新定时任务信息
    """
    # 获取定时任务信息
    db_job = get_job(db, job_id)
    if not db_job:
        raise NotFound(f"任务ID {job_id} 不存在")
    
    # 检查任务名称和组名是否已存在（如果修改了任务名称或组名）
    if (db_job.job_name != job_data.job_name or db_job.job_group != job_data.job_group) and \
       get_job_by_name_and_group(db, job_data.job_name, job_data.job_group):
        raise ValueError(f"任务名称 {job_data.job_name} 在组 {job_data.job_group} 中已存在")
    
    # 更新定时任务基本信息
    for key, value in job_data.dict(exclude={"job_id"}).items():
        if value is not None:
            setattr(db_job, key, value)
    
    # 提交事务
    db.commit()
    db.refresh(db_job)
    
    return db_job


def delete_job(db: Session, job_id: int) -> bool:
    """
    删除定时任务
    """
    # 获取定时任务信息
    db_job = get_job(db, job_id)
    if not db_job:
        raise NotFound(f"任务ID {job_id} 不存在")
    
    # 删除定时任务
    db.delete(db_job)
    db.commit()
    
    return True


def change_job_status(db: Session, job_id: int, status: str) -> Optional[SysJob]:
    """
    修改定时任务状态
    """
    # 获取定时任务信息
    db_job = get_job(db, job_id)
    if not db_job:
        raise NotFound(f"任务ID {job_id} 不存在")
    
    # 修改状态
    db_job.status = status
    
    # 提交事务
    db.commit()
    db.refresh(db_job)
    
    return db_job


def run_job(db: Session, job_id: int) -> bool:
    """
    立即执行一次任务
    """
    # 获取定时任务信息
    db_job = get_job(db, job_id)
    if not db_job:
        raise NotFound(f"任务ID {job_id} 不存在")
    
    # 执行任务逻辑（需要实现具体的任务执行器）
    # TODO: 实现任务执行逻辑
    
    return True


def get_job_logs(
    db: Session, 
    params: JobLogQuery
) -> Tuple[List[SysJobLog], int]:
    """
    获取定时任务日志列表（分页查询）
    """
    query = db.query(SysJobLog)
    
    # 构建查询条件
    if params.job_name:
        query = query.filter(SysJobLog.job_name.like(f"%{params.job_name}%"))
    if params.job_group:
        query = query.filter(SysJobLog.job_group == params.job_group)
    if params.status:
        query = query.filter(SysJobLog.status == params.status)
    if params.begin_time and params.end_time:
        query = query.filter(
            SysJobLog.create_time.between(params.begin_time, params.end_time)
        )
    
    # 统计总数
    total = query.count()
    
    # 排序和分页
    job_logs = query.order_by(SysJobLog.create_time.desc()).offset(
        (params.page_num - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return job_logs, total


def clean_job_logs(db: Session) -> bool:
    """
    清空定时任务日志
    """
    db.query(SysJobLog).delete()
    db.commit()
    return True 