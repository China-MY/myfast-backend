from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.online import SysUserOnline
from app.schemas.online import OnlineUserCreate, OnlineUserOut


class CRUDOnlineUser:
    """在线用户CRUD（不使用基类是因为这个表没有标准的更新操作）"""
    
    def get(self, db: Session, *, session_id: str) -> Optional[SysUserOnline]:
        """获取在线用户记录"""
        return db.query(SysUserOnline).filter(SysUserOnline.sessionId == session_id).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        user_name: str = None,
        ipaddr: str = None
    ) -> Dict[str, Any]:
        """获取在线用户列表"""
        query = db.query(SysUserOnline)
        
        # 过滤条件
        if user_name:
            query = query.filter(SysUserOnline.user_name.like(f"%{user_name}%"))
        
        if ipaddr:
            query = query.filter(SysUserOnline.ipaddr.like(f"%{ipaddr}%"))
        
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.order_by(SysUserOnline.last_access_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "items": items
        }
    
    def create(self, db: Session, *, obj_in: OnlineUserCreate) -> SysUserOnline:
        """创建在线用户记录"""
        db_obj = SysUserOnline(
            sessionId=obj_in.sessionId,
            user_id=obj_in.user_id,
            user_name=obj_in.user_name,
            ipaddr=obj_in.ipaddr,
            login_location=obj_in.login_location,
            browser=obj_in.browser,
            os=obj_in.os,
            status=obj_in.status,
            start_timestamp=obj_in.start_timestamp,
            last_access_time=obj_in.last_access_time,
            expire_time=obj_in.expire_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, session_id: str, obj_in: Dict[str, Any]) -> Optional[SysUserOnline]:
        """更新在线用户记录"""
        db_obj = self.get(db, session_id=session_id)
        if not db_obj:
            return None
        
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, session_id: str) -> Optional[SysUserOnline]:
        """删除在线用户记录"""
        db_obj = self.get(db, session_id=session_id)
        if not db_obj:
            return None
        
        db.delete(db_obj)
        db.commit()
        return db_obj
    
    def remove_multi(self, db: Session, *, session_ids: List[str]) -> int:
        """批量删除在线用户记录"""
        result = db.query(SysUserOnline).filter(SysUserOnline.sessionId.in_(session_ids)).delete(synchronize_session=False)
        db.commit()
        return result


online_user = CRUDOnlineUser() 