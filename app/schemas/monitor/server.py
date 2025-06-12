from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SysInfo(BaseModel):
    """系统信息"""
    os_name: str = Field("", description="操作系统名称")
    os_version: str = Field("", description="系统版本")
    hostname: str = Field("", description="主机名")
    ip: str = Field("", description="IP地址")
    python_version: str = Field("", description="Python版本")
    boot_time: str = Field("", description="启动时间")
    run_time: str = Field("", description="运行时间")


class CpuInfo(BaseModel):
    """CPU信息"""
    name: str = Field("", description="CPU名称")
    model: str = Field("", description="CPU型号")
    arch: str = Field("", description="CPU架构")
    cores: int = Field(0, description="CPU物理核心数")
    logical_cores: int = Field(0, description="CPU逻辑核心数")
    usage: float = Field(0.0, description="CPU使用率")


class MemInfo(BaseModel):
    """内存信息"""
    total: int = Field(0, description="总内存")
    used: int = Field(0, description="已用内存")
    free: int = Field(0, description="剩余内存")
    usage: float = Field(0.0, description="内存使用率")


class DiskInfo(BaseModel):
    """磁盘信息"""
    name: str = Field("", description="磁盘名称")
    mount_point: str = Field("", description="挂载点")
    fs_type: str = Field("", description="文件系统类型")
    total: int = Field(0, description="总容量")
    used: int = Field(0, description="已用容量")
    free: int = Field(0, description="剩余容量")
    usage: float = Field(0.0, description="使用率")


class NetworkInfo(BaseModel):
    """网络信息"""
    sent_bytes: int = Field(0, description="发送字节数")
    recv_bytes: int = Field(0, description="接收字节数")
    sent_packets: int = Field(0, description="发送数据包数")
    recv_packets: int = Field(0, description="接收数据包数")


class ServerInfo(BaseModel):
    """服务器信息"""
    cpu: CpuInfo = Field(default_factory=CpuInfo, description="CPU信息")
    mem: MemInfo = Field(default_factory=MemInfo, description="内存信息")
    sys: SysInfo = Field(default_factory=SysInfo, description="系统信息")
    disk: List[DiskInfo] = Field(default_factory=list, description="磁盘信息")
    network: NetworkInfo = Field(default_factory=NetworkInfo, description="网络信息")
    
    # 扁平化字段，便于前端直接使用
    # 系统信息
    os: Optional[str] = Field(None, description="操作系统")
    arch: Optional[str] = Field(None, description="系统架构")
    processor: Optional[str] = Field(None, description="处理器")
    hostname: Optional[str] = Field(None, description="主机名")
    ip: Optional[str] = Field(None, description="IP地址")
    boot_time: Optional[int] = Field(None, description="启动时间戳")
    
    # CPU信息
    cpu_percent: Optional[float] = Field(None, description="CPU使用率")
    cpu_count: Optional[int] = Field(None, description="CPU核心数")
    load_avg: Optional[List[float]] = Field(None, description="系统负载")
    
    # 内存信息
    total_memory: Optional[int] = Field(None, description="总内存")
    used_memory: Optional[int] = Field(None, description="已用内存")
    free_memory: Optional[int] = Field(None, description="空闲内存")
    memory_percent: Optional[float] = Field(None, description="内存使用率")
    
    # 磁盘信息汇总
    disk_total: Optional[int] = Field(None, description="磁盘总空间")
    disk_used: Optional[int] = Field(None, description="磁盘已用空间")
    disk_free: Optional[int] = Field(None, description="磁盘剩余空间")
    disk_percent: Optional[float] = Field(None, description="磁盘使用率")