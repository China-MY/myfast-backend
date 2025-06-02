from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.monitor.job import SysJob, SysJobLog
from app.domain.schemas.monitor.job import JobCreate, JobUpdate, JobInfo, JobQuery, JobLogQuery
from app.common.response import success, error, page
from app.service.monitor.job_service import (
    get_job, get_jobs, create_job, update_job, delete_job,
    change_job_status, run_job, get_job_logs, clean_job_logs
)

router = APIRouter()


@router.get("/list", summary="获取定时任务列表")
async def get_job_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: JobQuery = Depends(),
):
    """
    获取定时任务列表（分页查询）
    """
    try:
        jobs, total = get_jobs(db, params)
        job_list = [
            {
                "job_id": job.job_id,
                "job_name": job.job_name,
                "job_group": job.job_group,
                "job_params": job.job_params,
                "cron_expression": job.cron_expression,
                "misfire_policy": job.misfire_policy,
                "concurrent": job.concurrent,
                "status": job.status,
                "create_time": job.create_time,
                "remark": job.remark
            }
            for job in jobs
        ]
        return page(rows=job_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{job_id}", summary="获取定时任务详情")
async def get_job_info(
    job_id: int = Path(..., description="任务ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取定时任务详情
    """
    try:
        job = get_job(db, job_id)
        if not job:
            return error(msg="定时任务不存在", code=404)
        job_info = {
            "job_id": job.job_id,
            "job_name": job.job_name,
            "job_group": job.job_group,
            "job_params": job.job_params,
            "cron_expression": job.cron_expression,
            "misfire_policy": job.misfire_policy,
            "concurrent": job.concurrent,
            "status": job.status,
            "create_time": job.create_time,
            "remark": job.remark
        }
        return success(data=job_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加定时任务")
async def add_job(
    job_data: JobCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加定时任务
    """
    try:
        job = create_job(db, job_data)
        return success(msg="定时任务添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改定时任务")
async def edit_job(
    job_data: JobUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改定时任务
    """
    try:
        job = update_job(db, job_data.job_id, job_data)
        return success(msg="定时任务修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{job_id}", summary="删除定时任务")
async def remove_job(
    job_id: int = Path(..., description="任务ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除定时任务
    """
    try:
        result = delete_job(db, job_id)
        return success(msg="定时任务删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.put("/changeStatus", summary="修改任务状态")
async def change_status(
    job_id: int = Body(..., embed=True),
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改任务状态
    """
    try:
        job = change_job_status(db, job_id, status)
        return success(msg="任务状态修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.put("/run", summary="立即执行一次")
async def execute_job(
    job_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    立即执行一次任务
    """
    try:
        result = run_job(db, job_id)
        return success(msg="任务执行成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.get("/log/list", summary="获取定时任务日志列表")
async def get_job_log_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: JobLogQuery = Depends(),
):
    """
    获取定时任务日志列表（分页查询）
    """
    try:
        job_logs, total = get_job_logs(db, params)
        job_log_list = [
            {
                "job_log_id": job_log.job_log_id,
                "job_id": job_log.job_id,
                "job_name": job_log.job_name,
                "job_group": job_log.job_group,
                "job_params": job_log.job_params,
                "job_message": job_log.job_message,
                "status": job_log.status,
                "exception_info": job_log.exception_info,
                "create_time": job_log.create_time
            }
            for job_log in job_logs
        ]
        return page(rows=job_log_list, total=total)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/log/clean", summary="清空定时任务日志")
async def clean_all_job_logs(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    清空定时任务日志
    """
    try:
        result = clean_job_logs(db)
        return success(msg="定时任务日志清空成功")
    except Exception as e:
        return error(msg=str(e)) 