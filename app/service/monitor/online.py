from typing import List, Tuple, Optional
from datetime import datetime
import json
import traceback

from sqlalchemy.orm import Session

from app.models.system.user import SysUser
from app.schemas.monitor.online import OnlineUserOut
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
        self, 
        db: Session, skip: int = 0, limit: int = 100, 
        ipaddr: Optional[str] = None, username: Optional[str] = None
    ) -> Tuple[List[OnlineUserOut], int]:
        """
        获取在线用户列表
        """
        print(f"[DEBUG] 获取在线用户列表 - 参数: skip={skip}, limit={limit}, ipaddr={ipaddr}, username={username}")
        # 获取所有在线用户的token
        online_keys = redis_client.keys(f"{ONLINE_KEY_PREFIX}*")
        print(f"[DEBUG] 在线用户Redis键数量: {len(online_keys)}")
        online_users = []
        
        # 遍历所有token获取用户信息
        for key in online_keys:
            try:
                token = key.decode("utf-8").replace(ONLINE_KEY_PREFIX, "")
                user_data = redis_client.get(key)
                if not user_data:
                    print(f"[DEBUG] 键 {key} 的数据为空")
                    continue
                
                user_info = json.loads(user_data)
                print(f"[DEBUG] 解析用户数据: {user_info}")
                
                # 更新最后访问时间
                user_info['last_access_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                redis_client.setex(
                    key,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    json.dumps(user_info)
                )
                
                # 过滤条件
                if ipaddr and ipaddr not in str(user_info.get("ipaddr", "")):
                    continue
                
                # 检查用户名是否匹配（可能是user_name或username）
                user_name_value = user_info.get("user_name") or user_info.get("username", "")
                if username and username not in str(user_name_value):
                    continue
                
                # 处理日期时间字段
                login_time = user_info.get("login_time", "")
                last_access_time = user_info.get("last_access_time", login_time)
                
                # 确保字段名与OnlineUserOut模型匹配
                online_user_data = {
                    "sessionId": token,  # 会话ID就是token
                    "user_id": user_info.get("user_id"),
                    "user_name": user_name_value,
                    "ipaddr": user_info.get("ipaddr", ""),
                    "login_location": user_info.get("login_location", ""),
                    "browser": user_info.get("browser", "Unknown"),
                    "os": user_info.get("os", "Unknown"),
                    "status": user_info.get("status", "on_line"),
                    "start_timestamp": login_time,
                    "last_access_time": last_access_time,
                    "expire_time": user_info.get("expire_time", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                }
                
                print(f"[DEBUG] 创建在线用户对象: {online_user_data}")
                online_users.append(OnlineUserOut(**online_user_data))
            except Exception as e:
                print(f"[DEBUG] 解析在线用户数据出错: {str(e)}")
                print(traceback.format_exc())
        
        # 排序和分页
        online_users.sort(key=lambda x: x.start_timestamp if x.start_timestamp else "", reverse=True)
        total = len(online_users)
        
        print(f"[DEBUG] 在线用户总数: {total}")
        
        # 分页处理
        if skip < total:
            end = min(skip + limit, total)
            result_users = online_users[skip:end]
        else:
            result_users = []
        
        print(f"[DEBUG] 返回用户数量: {len(result_users)}")
        return result_users, total
    
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
        try:
            # 先清理该用户之前的会话
            self._clean_previous_sessions(user.user_id)
            
            location = get_location_by_ip(ip_addr)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建在线用户信息
            online_user = {
                "user_id": user.user_id,
                "user_name": user.username,
                "ipaddr": ip_addr,
                "login_location": location,
                "browser": "Unknown",  # 实际应用中应从请求头获取
                "os": "Unknown",       # 实际应用中应从请求头获取
                "status": "on_line",
                "login_time": current_time,
                "expire_time": settings.ACCESS_TOKEN_EXPIRE_MINUTES
            }
            
            print(f"[DEBUG] 保存在线用户: {token[:10]}..., 用户ID: {user.user_id}, 用户名: {user.username}")
            
            # 存储到Redis，设置过期时间与token一致
            key = f"{ONLINE_KEY_PREFIX}{token}"
            redis_client.setex(
                key, 
                settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                json.dumps(online_user)
            )
        except Exception as e:
            print(f"[ERROR] 保存在线用户出错: {str(e)}")
            print(traceback.format_exc())
            
    def _clean_previous_sessions(self, user_id: int) -> None:
        """
        清理用户之前的会话
        """
        try:
            # 获取所有在线用户的token
            online_keys = redis_client.keys(f"{ONLINE_KEY_PREFIX}*")
            count = 0
            
            # 遍历查找该用户的旧会话并删除
            for key in online_keys:
                user_data = redis_client.get(key)
                if not user_data:
                    continue
                
                try:
                    user_info = json.loads(user_data)
                    if user_info.get("user_id") == user_id:
                        token = key.decode("utf-8").replace(ONLINE_KEY_PREFIX, "")
                        print(f"[DEBUG] 清理用户ID {user_id} 的旧会话: {token[:10]}...")
                        redis_client.delete(key)
                        count += 1
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                
            if count > 0:
                print(f"[INFO] 已清理用户ID {user_id} 的 {count} 个旧会话")
        except Exception as e:
            print(f"[ERROR] 清理用户旧会话出错: {str(e)}")
            # 不阻止主流程执行
    
    def remove_online_user(self, token: str) -> None:
        """
        移除在线用户
        """
        key = f"{ONLINE_KEY_PREFIX}{token}"
        if redis_client.exists(key):
            redis_client.delete(key)


# 实例化服务
online_service = OnlineService() 