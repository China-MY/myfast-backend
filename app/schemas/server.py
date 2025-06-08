from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SysInfo(BaseModel):
    """系统信息"""
    computer_name: str = Field("", description="服务器名称")
    computer_ip: str = Field("", description="服务器IP")
    user_dir: str = Field("", description="项目路径")
    os_name: str = Field("", description="操作系统")
    os_arch: str = Field("", description="系统架构")


class CpuInfo(BaseModel):
    """CPU信息"""
    cpu_num: int = Field(0, description="CPU核心数")
    used: float = Field(0.0, description="CPU使用率")
    sys: float = Field(0.0, description="系统CPU使用率")
    user: float = Field(0.0, description="用户CPU使用率")
    wait: float = Field(0.0, description="等待IO的CPU时间占比")
    free: float = Field(0.0, description="空闲CPU占比")


class MemInfo(BaseModel):
    """内存信息"""
    total: int = Field(0, description="总内存")
    used: int = Field(0, description="已用内存")
    free: int = Field(0, description="剩余内存")
    usage: float = Field(0.0, description="内存使用率")


class DiskInfo(BaseModel):
    """磁盘信息"""
    total: int = Field(0, description="总容量")
    used: int = Field(0, description="已用容量")
    free: int = Field(0, description="剩余容量")
    usage: float = Field(0.0, description="使用率")


class NetworkInfo(BaseModel):
    """网络信息"""
    name: str = Field("", description="网卡名称")
    address: str = Field("", description="IP地址")
    netmask: str = Field("", description="子网掩码")
    broadcast: str = Field("", description="广播地址")
    sent_bytes: int = Field(0, description="发送字节数")
    recv_bytes: int = Field(0, description="接收字节数")
    sent_packets: int = Field(0, description="发送数据包数")
    recv_packets: int = Field(0, description="接收数据包数")
    err_in: int = Field(0, description="接收错误数")
    err_out: int = Field(0, description="发送错误数")
    drop_in: int = Field(0, description="接收丢包数")
    drop_out: int = Field(0, description="发送丢包数")


class SysFileInfo(BaseModel):
    """系统文件信息"""
    dir_name: str = Field("", description="盘符路径")
    sys_type_name: str = Field("", description="文件系统")
    type_name: str = Field("", description="文件类型")
    total: str = Field("0", description="总大小")
    free: str = Field("0", description="剩余大小")
    used: str = Field("0", description="已用大小")
    usage: str = Field("0%", description="使用率")


class ServerInfo(BaseModel):
    """服务器信息"""
    cpu: CpuInfo = Field(default_factory=CpuInfo, description="CPU信息")
    mem: MemInfo = Field(default_factory=MemInfo, description="内存信息")
    sys: SysInfo = Field(default_factory=SysInfo, description="系统信息")
    disk: DiskInfo = Field(default_factory=DiskInfo, description="磁盘信息")
    sys_files: List[SysFileInfo] = Field(default_factory=list, description="系统文件信息")
    networks: List[NetworkInfo] = Field(default_factory=list, description="网络信息") 