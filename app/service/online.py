from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.models.user import SysUser
from app.schemas.online import OnlineUserOut
from app.core.redis import redis_client
from app.utils.ip import get_location_by_ip
from app.core.config import settings

# Redis键前缀
ONLINE_KEY_PREFIX = "online:token:"


class OnlineService:
    """
    在线用户服务
    """
    
    def get_online_users(
        self, db: Session, skip: int = 0, limit: int = 100, 
        ipaddr: Optional[str] = None, username: Optional[str] = None
    ) -> Tuple[List[OnlineUserOut], int]:
        """
        获取在线用户列表
        """
        # 获取所有在线用户的token
        online_keys = redis_client.keys(f"{ONLINE_KEY_PREFIX}*")
        online_users = []
        
        # 遍历所有token获取用户信息
        for key in online_keys:
            user_data = redis_client.get(key)
            if not user_data:
                continue
            
            try:
                user_info = json.loads(user_data)
                
                # 过滤条件
                if ipaddr and ipaddr not in user_info.get("ipaddr", ""):
                    continue
                if username and username not in user_info.get("username", ""):
                    continue
                
                online_users.append(OnlineUserOut(**user_info))
            except Exception as e:
                print(f"解析在线用户数据出错: {e}")
        
        # 排序和分页
        online_users.sort(key=lambda x: x.login_time, reverse=True)
        total = len(online_users)
        
        # 分页处理
        if skip < total:
            end = min(skip + limit, total)
            online_users = online_users[skip:end]
        else:
            online_users = []
        
        return online_users, total
    
    def is_current_user_token(self, token: str, current_user: SysUser) -> bool:
        """
        检查是否是当前用户的token
        """
        user_data = redis_client.get(f"{ONLINE_KEY_PREFIX}{token}")
        if not user_data:
            return False
        
        try:
            user_info = json.loads(user_data)
            return user_info.get("user_id") == current_user.user_id
        except:
            return False
    
    def force_logout(self, db: Session, token: str) -> bool:
        """
        强制用户退出登录
        """
        key = f"{ONLINE_KEY_PREFIX}{token}"
        if redis_client.exists(key):
            redis_client.delete(key)
            return True
        return False
    
    def batch_force_logout(self, db: Session, tokens: List[str]) -> int:
        """
        批量强制用户退出登录
        """
        count = 0
        for token in tokens:
            if self.force_logout(db, token):
                count += 1
        return count
    
    def save_online_user(self, token: str, user: SysUser, ip_addr: str) -> None:
        """
        保存在线用户信息
        """
        location = get_location_by_ip(ip_addr)
        
        # 构建在线用户信息
        online_user = {
            "token": token,
            "user_id": user.user_id,
            "username": user.username,
            "user_name": user.nick_name or user.username,
            "ipaddr": ip_addr,
            "login_location": location,
            "browser": "Unknown",  # 实际应用中应从请求头获取
            "os": "Unknown",       # 实际应用中应从请求头获取
            "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 存储到Redis，设置过期时间与token一致
        key = f"{ONLINE_KEY_PREFIX}{token}"
        redis_client.setex(
            key, 
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            json.dumps(online_user)
        )
    
    def remove_online_user(self, token: str) -> None:
        """
        移除在线用户
        """
        key = f"{ONLINE_KEY_PREFIX}{token}"
        if redis_client.exists(key):
            redis_client.delete(key)


# 实例化服务
online_service = OnlineService() 