import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.crud.monitor.job import job as job_crud, job_log as job_log_crud
from app.models.monitor.job import SysJob, SysJobLog
from app.schemas.monitor.job import JobCreate, JobUpdate, JobLogCreate


class JobService:
    """任务调度服务"""
    
    def get_job_by_id(self, db: Session, job_id: int) -> Optional[SysJob]:
        """根据ID获取任务信息"""
        return job_crud.get(db, id=job_id)
    
    def get_job(self, db: Session, job_id: int) -> Optional[SysJob]:
        """获取任务信息"""
        return job_crud.get(db, id=job_id)
    
    def get_jobs(
        self, 
        db: Session, 
        skip: int = 0,
        limit: int = 10,
        job_name: str = None, 
        job_group: str = None, 
        status: str = None
    ) -> Tuple[List[SysJob], int]:
        """获取任务列表"""
        print(f"[DEBUG] service.get_jobs - 参数: skip={skip}, limit={limit}, job_name={job_name}, job_group={job_group}, status={status}")
        result = job_crud.search_by_keyword(
            db,
            job_name=job_name,
            job_group=job_group,
            status=status,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
        print(f"[DEBUG] service.get_jobs - 结果类型: items={type(result['items'])}, 第一条={type(result['items'][0]) if result['items'] else 'None'}")
        return result["items"], result["total"]
    
    def get_job_list(
        self, 
        db: Session, 
        keyword: str = None,
        job_name: str = None, 
        job_group: str = None, 
        status: str = None,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取任务列表"""
        result = job_crud.search_by_keyword(
            db,
            keyword=keyword,
            job_name=job_name,
            job_group=job_group,
            status=status,
            page=page,
            page_size=page_size
        )
        return result
    
    def create_job(self, db: Session, obj_in: JobCreate, current_user_id: int) -> SysJob:
        """创建任务"""
        return job_crud.create_with_user(db, obj_in=obj_in, user_id=current_user_id)
    
    def update_job(self, db: Session, job_id: int, obj_in: JobUpdate, current_user_id: int) -> Optional[SysJob]:
        """更新任务"""
        db_obj = job_crud.get(db, id=job_id)
        if not db_obj:
            return None
        return job_crud.update_with_user(db, db_obj=db_obj, obj_in=obj_in, user_id=current_user_id)
    
    def delete_job(self, db: Session, job_id: int) -> Optional[SysJob]:
        """删除任务"""
        return job_crud.remove(db, id=job_id)
    
    def batch_delete_jobs(self, db: Session, job_ids: List[int]) -> int:
        """批量删除任务"""
        return job_crud.remove_multi(db, ids=job_ids)
    
    def update_job_status(self, db: Session, job_id: int, status: str, current_user_name: str) -> Optional[SysJob]:
        """更新任务状态"""
        return job_crud.update_status(db, job_id=job_id, status=status, update_by=current_user_name)
    
    def run_job(self, db: Session, job_id: int) -> Dict[str, Any]:
        """立即执行任务"""
        db_obj = job_crud.get(db, id=job_id)
        if not db_obj:
            return {"success": False, "message": "任务不存在"}
        
        # 创建任务日志（移除不存在的字段）
        job_log_obj = JobLogCreate(
            # job_id字段在数据库中不存在，移除
            # job_id=job_id,
            job_name=db_obj.job_name,
            job_group=db_obj.job_group,
            invoke_target=db_obj.invoke_target,
            # start_time字段在数据库中不存在，移除
            # start_time=datetime.now()
        )
        
        # 记录执行开始
        job_log = job_log_crud.create(db, obj_in=job_log_obj)
        
        try:
            # 这里只是模拟执行任务，实际应该根据invoke_target执行相应的函数
            # 例如：通过importlib动态导入模块并执行函数
            time.sleep(1)  # 模拟任务执行
            
            # 更新任务日志（移除不存在的字段）
            # job_log.end_time = datetime.now()  # end_time字段在数据库中不存在，移除
            job_log.status = "0"  # 成功
            job_log.job_message = "执行成功"
            db.add(job_log)
            db.commit()
            db.refresh(job_log)
            
            return {"success": True, "message": "任务执行成功"}
        except Exception as e:
            # 更新任务日志（移除不存在的字段）
            # job_log.end_time = datetime.now()  # end_time字段在数据库中不存在，移除
            job_log.status = "1"  # 失败
            job_log.job_message = "执行失败"
            job_log.exception_info = str(e)
            db.add(job_log)
            db.commit()
            db.refresh(job_log)
            
            return {"success": False, "message": f"任务执行失败: {str(e)}"}
    
    def get_job_logs(
        self, 
        db: Session, 
        skip: int = 0,
        limit: int = 10,
        job_name: str = None, 
        job_group: str = None,
        job_id: int = None,
        status: str = None
    ) -> Tuple[List[SysJobLog], int]:
        """获取任务日志列表"""
        print(f"[DEBUG] JobService.get_job_logs - 参数: job_name={job_name}, job_group={job_group}, job_id={job_id}, status={status}")
        result = job_log_crud.search_by_keyword(
            db,
            job_name=job_name,
            job_group=job_group,
            status=status,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
        
        return result["items"], result["total"]
    
    def get_job_log_list(
        self, 
        db: Session, 
        job_name: str = None, 
        job_group: str = None, 
        status: str = None,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取任务日志列表"""
        result = job_log_crud.search_by_keyword(
            db,
            job_name=job_name,
            job_group=job_group,
            status=status,
            page=page,
            page_size=page_size
        )
        
        return result
    
    def clean_job_logs(self, db: Session) -> int:
        """清空任务日志"""
        return job_log_crud.clean(db)

    def run_job_once(self, db: Session, job_id: int) -> Dict[str, Any]:
        """立即执行一次任务"""
        return self.run_job(db, job_id=job_id)
    
    def clean_all_job_logs(self, db: Session) -> int:
        """清空所有任务日志"""
        return self.clean_job_logs(db)

    def change_job_status(self, db: Session, job_id: int, status: str, updater_id: int) -> Optional[SysJob]:
        """修改任务状态"""
        # 获取用户名
        db_obj = job_crud.get(db, id=job_id)
        if not db_obj:
            return None
        
        # 更新状态
        db_obj.status = status
        db_obj.update_by = str(updater_id)
        db_obj.update_time = datetime.now()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


job_service = JobService() 