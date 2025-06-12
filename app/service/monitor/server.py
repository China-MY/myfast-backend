import os
import platform
import socket
import time
import psutil
from datetime import datetime
from typing import List, Optional

from app.schemas.monitor.server import (
    ServerInfo, CpuInfo, MemInfo, DiskInfo, 
    SysInfo, NetworkInfo
)


class ServerService:
    """
    服务器监控服务
    """
    
    def get_server_info(self) -> ServerInfo:
        """
        获取服务器基本信息
        """
        cpu_info = self._get_cpu_info()
        mem_info = self._get_mem_info()
        sys_info = self._get_sys_info()
        disk_info_list = self._get_disk_info()
        network_info = self._get_network_info()
        
        # 创建扁平化的服务器信息，前端更容易处理
        result = ServerInfo(
            cpu=cpu_info,
            mem=mem_info,
            sys=sys_info,
            disk=disk_info_list,
            network=network_info
        )
        
        # 添加扁平化的属性，便于前端直接访问
        # 系统信息
        result.os = sys_info.os_name
        result.arch = cpu_info.arch
        result.processor = cpu_info.model or cpu_info.name
        result.hostname = sys_info.hostname
        result.ip = sys_info.ip
        result.boot_time = int(datetime.strptime(sys_info.boot_time, "%Y-%m-%d %H:%M:%S").timestamp()) if sys_info.boot_time else None
        
        # CPU信息
        result.cpu_percent = cpu_info.usage
        result.cpu_count = cpu_info.cores
        result.load_avg = self._get_load_average()
        
        # 内存信息
        result.total_memory = mem_info.total
        result.used_memory = mem_info.used
        result.free_memory = mem_info.free
        result.memory_percent = mem_info.usage
        
        # 磁盘信息 (汇总所有磁盘)
        result.disk_total = sum(d.total for d in disk_info_list) if disk_info_list else 0
        result.disk_used = sum(d.used for d in disk_info_list) if disk_info_list else 0
        result.disk_free = sum(d.free for d in disk_info_list) if disk_info_list else 0
        # 计算平均磁盘使用率
        if result.disk_total > 0:
            result.disk_percent = (result.disk_used / result.disk_total) * 100
        else:
            result.disk_percent = 0
        
        return result
    
    def _get_cpu_info(self) -> CpuInfo:
        """
        获取CPU信息
        """
        cpu_count = psutil.cpu_count(logical=False)
        logical_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        
        return CpuInfo(
            name=platform.processor(),
            arch=platform.machine(),
            cores=cpu_count,
            logical_cores=logical_count,
            usage=cpu_usage,
            model=self._get_cpu_model()
        )
    
    def _get_cpu_model(self) -> str:
        """
        获取CPU型号
        """
        if platform.system() == "Windows":
            return platform.processor()
        elif platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            except:
                pass
        return platform.processor()
    
    def _get_mem_info(self) -> MemInfo:
        """
        获取内存信息
        """
        mem = psutil.virtual_memory()
        
        return MemInfo(
            total=mem.total,
            used=mem.used,
            free=mem.available,
            usage=mem.percent
        )
    
    def _get_sys_info(self) -> SysInfo:
        """
        获取系统信息
        """
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        
        return SysInfo(
            os_name=platform.system(),
            os_version=platform.version(),
            hostname=socket.gethostname(),
            ip=self._get_host_ip(),
            python_version=platform.python_version(),
            boot_time=boot_time,
            run_time=self._get_run_time(psutil.boot_time())
        )
    
    def _get_host_ip(self) -> str:
        """
        获取主机IP
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_run_time(self, boot_time: float) -> str:
        """
        获取运行时间
        """
        now = time.time()
        run_seconds = int(now - boot_time)
        
        days, remainder = divmod(run_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天{hours}小时{minutes}分钟"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def _get_disk_info(self) -> List[DiskInfo]:
        """
        获取磁盘信息
        """
        disk_info = []
        
        for part in psutil.disk_partitions():
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    # 跳过CD-ROM驱动器
                    continue
            
            usage = psutil.disk_usage(part.mountpoint)
            
            disk_info.append(
                DiskInfo(
                    name=part.device,
                    mount_point=part.mountpoint,
                    fs_type=part.fstype,
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    usage=usage.percent
                )
            )
        
        return disk_info
    
    def _get_network_info(self) -> NetworkInfo:
        """
        获取网络信息
        """
        net_io = psutil.net_io_counters()
        
        return NetworkInfo(
            sent_bytes=net_io.bytes_sent,
            recv_bytes=net_io.bytes_recv,
            sent_packets=net_io.packets_sent,
            recv_packets=net_io.packets_recv
        )
    
    def _get_load_average(self) -> Optional[List[float]]:
        """
        获取系统负载
        """
        try:
            if platform.system() == "Windows":
                # Windows系统没有原生的load average，使用CPU使用率代替
                return [psutil.cpu_percent(interval=0.1)]
            else:
                # Linux/Unix系统获取1分钟、5分钟、15分钟的负载
                return list(os.getloadavg())
        except:
            return None


# 实例化服务
server_service = ServerService() 