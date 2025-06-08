from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.job import SysJob, SysJobLog
from app.schemas.job import JobCreate, JobUpdate, JobLogCreate


class CRUDJob(CRUDBase[SysJob, JobCreate, JobUpdate]):
    """任务调度CRUD"""
    
    def get_by_name_and_group(self, db: Session, *, job_name: str, job_group: str) -> Optional[SysJob]:
        """通过任务名称和组名获取任务"""
        return db.query(self.model).filter(
            self.model.job_name == job_name,
            self.model.job_group == job_group
        ).first()
    
    def search_by_keyword(
        self, 
        db: Session, 
        *, 
        keyword: str = None,
        job_name: str = None, 
        job_group: str = None, 
        status: str = None,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """搜索任务"""
        query = db.query(self.model)
        
        # 搜索条件
        if keyword:
            query = query.filter(
                (self.model.job_name.like(f"%{keyword}%")) | 
                (self.model.job_group.like(f"%{keyword}%")) |
                (self.model.invoke_target.like(f"%{keyword}%"))
            )
        
        if job_name:
            query = query.filter(self.model.job_name.like(f"%{job_name}%"))
        
        if job_group:
            query = query.filter(self.model.job_group == job_group)
            
        if status:
            query = query.filter(self.model.status == status)
            
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(self.model.job_id).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items
        }
    
    def update_status(self, db: Session, *, job_id: int, status: str, update_by: str) -> Optional[SysJob]:
        """更新任务状态"""
        db_obj = self.get(db, id=job_id)
        if not db_obj:
            return None
        
        db_obj.status = status
        db_obj.update_by = update_by
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDJobLog(CRUDBase[SysJobLog, JobLogCreate, Any]):
    """任务日志CRUD"""
    
    def search_by_keyword(
        self, 
        db: Session, 
        *, 
        job_name: str = None, 
        job_group: str = None, 
        status: str = None,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """搜索任务日志"""
        query = db.query(self.model)
        
        # 搜索条件
        if job_name:
            query = query.filter(self.model.job_name.like(f"%{job_name}%"))
        
        if job_group:
            query = query.filter(self.model.job_group == job_group)
            
        if status:
            query = query.filter(self.model.status == status)
            
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(self.model.job_log_id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items
        }
    
    def clean(self, db: Session) -> int:
        """清空任务日志"""
        result = db.query(self.model).delete(synchronize_session=False)
        db.commit()
        return result


job = CRUDJob(SysJob)
job_log = CRUDJobLog(SysJobLog) 