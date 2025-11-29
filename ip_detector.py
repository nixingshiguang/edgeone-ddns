#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公网IP检测模块
"""

import socket
import requests
import logging
import time
from typing import Optional, List

class IPDetector:
    """公网IP检测器"""
    
    def __init__(self):
        # IPv4检测服务
        self.ipv4_services = [
            {
                'name': 'nxsg-ipv4',
                'url': 'https://ipv4.nxsg.dpdns.org/',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'ipip-net',
                'url': 'https://myip.ipip.net',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'oray-checkip',
                'url': 'https://ddns.oray.com/checkip',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': '3322-net',
                'url': 'https://ip.3322.net',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'ipw-cn-v4',
                'url': 'https://4.ipw.cn',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'yinghualuo-v4',
                'url': 'https://v4.yinghualuo.cn/bejson',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            }
        ]
        
        # IPv6检测服务
        self.ipv6_services = [
            {
                'name': 'nxsg-ipv6',
                'url': 'https://ipv6.nxsg.dpdns.org/',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'neu6-edu',
                'url': 'https://speed.neu6.edu.cn/getIP.php',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'ident-me-v6',
                'url': 'https://v6.ident.me',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'ipw-cn-v6',
                'url': 'https://6.ipw.cn',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            },
            {
                'name': 'yinghualuo-v6',
                'url': 'https://v6.yinghualuo.cn/bejson',
                'extract': lambda data: data.strip() if isinstance(data, str) else None
            }
        ]
    
    def get_public_ip(self, service_index: int = 0, ip_version: str = 'ipv4') -> Optional[str]:
        """获取公网IP地址"""
        services = self.ipv4_services if ip_version == 'ipv4' else self.ipv6_services
        
        if service_index >= len(services):
            return None
        
        service = services[service_index]
        
        try:
            logging.debug(f"尝试使用 {service['name']} 获取{ip_version.upper()}公网IP...")
            
            response = requests.get(
                service['url'], 
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            # 尝试解析JSON
            try:
                data = response.json()
            except:
                # 如果不是JSON，使用原始文本
                data = response.text.strip()
            
            ip = service['extract'](data)
            
            if ip and self._is_valid_ip(ip, ip_version):
                logging.info(f"成功获取{ip_version.upper()}公网IP: {ip} (来源: {service['name']})")
                return ip
            else:
                logging.warning(f"{service['name']} 返回的{ip_version.upper()} IP无效: {ip}")
                
        except requests.exceptions.RequestException as e:
            logging.warning(f"使用 {service['name']} 获取{ip_version.upper()} IP失败: {str(e)}")
        except Exception as e:
            logging.warning(f"解析 {service['name']} 响应失败: {str(e)}")
        
        # 尝试下一个服务
        return self.get_public_ip(service_index + 1, ip_version)
    
    def get_ipv4(self) -> Optional[str]:
        """获取IPv4公网地址"""
        return self.get_public_ip(ip_version='ipv4')
    
    def get_ipv6(self) -> Optional[str]:
        """获取IPv6公网地址"""
        return self.get_public_ip(ip_version='ipv6')
    
    def _is_valid_ip(self, ip: str, ip_version: str = 'ipv4') -> bool:
        """验证IP地址格式"""
        try:
            if ip_version == 'ipv4':
                # IPv4验证
                socket.inet_aton(ip)
                parts = ip.split('.')
                if len(parts) != 4:
                    return False
                
                # 排除私有IP地址范围
                first_octet = int(parts[0])
                second_octet = int(parts[1])
                
                # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
                if (first_octet == 10 or 
                    (first_octet == 172 and 16 <= second_octet <= 31) or
                    (first_octet == 192 and second_octet == 168)):
                    return False
                
                # 排除环回地址和其他保留地址
                if first_octet == 127 or first_octet == 169:
                    return False
                
                return True
            else:
                # IPv6验证
                socket.inet_pton(socket.AF_INET6, ip)
                # 简单的IPv6私有地址检查
                if ip.startswith('fd') or ip.startswith('fc'):
                    return False
                # 排除环回地址
                if ip == '::1':
                    return False
                
                return True
            
        except socket.error:
            return False
        except ValueError:
            return False
        except:
            return False
    
    def get_local_ip(self) -> Optional[str]:
        """获取本地IP地址"""
        try:
            # 创建UDP socket连接到公网地址
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception as e:
            logging.warning(f"获取本地IP失败: {str(e)}")
            return None
    
    def check_ip_change(self, current_ip: str, previous_ip: Optional[str] = None) -> bool:
        """检查IP是否发生变化"""
        if previous_ip is None:
            return True
        
        return current_ip != previous_ip
    
    def get_all_ips(self, ipv4_enabled: bool = True, ipv6_enabled: bool = False) -> dict:
        """获取所有IP信息"""
        result = {
            'local_ip': self.get_local_ip(),
            'timestamp': int(time.time())
        }
        
        if ipv4_enabled:
            result['ipv4'] = self.get_ipv4()
            
        if ipv6_enabled:
            result['ipv6'] = self.get_ipv6()
            
        # 保持向后兼容性
        if ipv4_enabled:
            result['public_ip'] = result['ipv4']
        
        return result