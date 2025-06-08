import socket
import requests
from typing import Dict, Any, Optional


def get_location_by_ip(ip: str) -> str:
    """
    根据IP地址获取地理位置
    
    Args:
        ip: IP地址
    
    Returns:
        地理位置字符串
    """
    # 如果是本地IP，直接返回
    if ip in ("127.0.0.1", "localhost", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
        return "内网IP"
    
    try:
        # 尝试使用淘宝IP接口
        response = requests.get(f"http://ip.taobao.com/outGetIpInfo?ip={ip}&accessKey=alibaba-inc", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 0:
                country = data["data"]["country"] or ""
                region = data["data"]["region"] or ""
                city = data["data"]["city"] or ""
                
                location = country
                if region and region != country:
                    location += " " + region
                if city and city != region:
                    location += " " + city
                
                return location or "未知位置"
    except:
        pass
    
    try:
        # 备用方案：使用ip-api.com
        response = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                country = data["country"] or ""
                region = data["regionName"] or ""
                city = data["city"] or ""
                
                location = country
                if region and region != country:
                    location += " " + region
                if city and city != region:
                    location += " " + city
                
                return location or "未知位置"
    except:
        pass
    
    return "未知位置"


def get_host_ip() -> str:
    """
    获取本机IP地址
    
    Returns:
        本机IP地址
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1" 