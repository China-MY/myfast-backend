from typing import Dict, Any
from fastapi import APIRouter, Depends
import platform
import psutil
import socket
import datetime
import time
from app.common.response import success, error
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser

router = APIRouter()


@router.get("/info", summary="获取服务器信息")
async def get_server_info(
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取服务器信息（CPU、内存、磁盘、系统等信息）
    """
    try:
        # 系统信息
        sys_info = {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_arch": platform.machine(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
            "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "server_uptime": get_uptime()
        }
        
        # CPU信息
        cpu_info = {
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_logical_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_freq": get_cpu_freq()
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            "total": bytes_to_human(memory.total),
            "used": bytes_to_human(memory.used),
            "free": bytes_to_human(memory.available),
            "percent": memory.percent
        }
        
        # 磁盘信息
        disk_info = []
        for part in psutil.disk_partitions():
            if part.mountpoint:
                usage = psutil.disk_usage(part.mountpoint)
                disk_info.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": bytes_to_human(usage.total),
                    "used": bytes_to_human(usage.used),
                    "free": bytes_to_human(usage.free),
                    "percent": usage.percent
                })
        
        # 网络信息
        net_io = psutil.net_io_counters()
        net_info = {
            "bytes_sent": bytes_to_human(net_io.bytes_sent),
            "bytes_recv": bytes_to_human(net_io.bytes_recv),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "dropin": net_io.dropin,
            "dropout": net_io.dropout
        }
        
        return success(data={
            "sys": sys_info,
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "net": net_info
        })
    except Exception as e:
        return error(msg=str(e))


def bytes_to_human(n: int) -> str:
    """
    将字节数转换为人类可读的字符串
    """
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i * 10)
    
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f"{value:.2f} {s}"
    
    return f"{n} B"


def get_uptime() -> str:
    """
    获取系统运行时间
    """
    uptime = time.time() - psutil.boot_time()
    days = int(uptime // 86400)
    hours = int((uptime % 86400) // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    if days > 0:
        return f"{days}天 {hours}小时 {minutes}分钟 {seconds}秒"
    elif hours > 0:
        return f"{hours}小时 {minutes}分钟 {seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟 {seconds}秒"
    else:
        return f"{seconds}秒"


def get_cpu_freq() -> Dict[str, Any]:
    """
    获取CPU频率信息
    """
    try:
        freq = psutil.cpu_freq()
        if freq:
            return {
                "current": f"{freq.current:.2f} MHz" if freq.current else "N/A",
                "min": f"{freq.min:.2f} MHz" if freq.min else "N/A",
                "max": f"{freq.max:.2f} MHz" if freq.max else "N/A"
            }
        else:
            return {"current": "N/A", "min": "N/A", "max": "N/A"}
    except Exception:
        return {"current": "N/A", "min": "N/A", "max": "N/A"}