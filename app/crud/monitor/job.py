from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.utils.base import CRUDBase
from app.models.monitor.job import SysJob, SysJobLog
from app.schemas.monitor.job import JobCreate, JobUpdate, JobLogCreate


class CRUDJob(CRUDBase[SysJob, JobCreate, JobUpdate]):
    """任务调度CRUD"""
    
    def get_by_name_and_group(self, db: Session, *, job_name: str, job_group: str) -> Optional[SysJob]:
        """通过任务名称和组名获取任务"""
        return db.query(self.model).filter(
            self.model.job_name == job_name,
            self.model.job_group == job_group
        ).first()
    
    def create_with_user(self, db: Session, *, obj_in: JobCreate, user_id: int) -> SysJob:
        """创建任务并记录创建者"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_obj.create_by = str(user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_user(self, db: Session, *, db_obj: SysJob, obj_in: Union[JobUpdate, Dict[str, Any]], user_id: int) -> SysJob:
        """更新任务并记录更新者"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db_obj.update_by = str(user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
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
        print(f"[DEBUG] CRUDJob.search_by_keyword - 参数: keyword={keyword}, job_name={job_name}, job_group={job_group}, status={status}, page={page}, page_size={page_size}")
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
        print(f"[DEBUG] CRUDJob.search_by_keyword - 数据总数: {total}")
        
        # 分页
        items = query.order_by(self.model.job_id).offset((page - 1) * page_size).limit(page_size).all()
        print(f"[DEBUG] CRUDJob.search_by_keyword - 返回数据条数: {len(items)}, 第一条数据类型: {type(items[0]) if items else 'None'}")

        if items and items[0] is not None:
            print(f"[DEBUG] 第一条任务属性: {items[0].__dict__ if hasattr(items[0], '__dict__') else items[0]}")
        
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
        job_id: int = None,
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
            
        # job_id字段在sys_job_log表中不存在，暂时注释掉
        # if job_id:
        #     query = query.filter(self.model.job_id == job_id)
            
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