#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import json
import logging
from typing import List, Optional, Dict

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.data = {
            'secret_id': '',
            'secret_key': '',
            'zone_id': '',
            'domains': [],  # 保持向后兼容
            'ipv4_domains': [],  # IPv4域名列表
            'ipv6_domains': [],  # IPv6域名列表
            'wechat_webhook': '',
            'update_interval': 300,  # 5分钟
            'log_level': 'INFO',
            'ipv4_enabled': False,  # 默认禁用IPv4，需要用户主动选择
            'ipv6_enabled': False,  # 默认禁用IPv6，需要用户主动选择
            # 自定义Webhook通知配置
            'webhook_enabled': False,
            'webhook_url': '',
            'webhook_headers': '{}',  # JSON字符串
            'webhook_body_template': '{}'  # JSON字符串，包含变量占位符
        }
        
    def load(self) -> bool:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
                logging.info(f"配置文件加载成功: {self.config_file}")
                return True
            else:
                logging.info(f"配置文件不存在，使用默认配置: {self.config_file}")
                return False
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            return False
    
    def save(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logging.info(f"配置文件保存成功: {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def is_valid(self) -> bool:
        """验证配置是否有效"""
        required_fields = ['secret_id', 'secret_key', 'zone_id']
        return all(self.data.get(field) for field in required_fields)
    
    def to_dict(self) -> dict:
        """返回配置字典（隐藏敏感信息）"""
        result = self.data.copy()
        # 隐藏密钥信息 - 只有当secret_key不为空且不是已经是掩码时才隐藏
        secret_key = result.get('secret_key', '')
        if secret_key and not secret_key.startswith('*'):
            result['secret_key'] = '*' * 20
        return result
    
    # 属性访问器
    @property
    def secret_id(self) -> str:
        return self.data.get('secret_id', '')
    
    @secret_id.setter
    def secret_id(self, value: str):
        self.data['secret_id'] = value.strip()
    
    @property
    def secret_key(self) -> str:
        return self.data.get('secret_key', '')
    
    @secret_key.setter
    def secret_key(self, value: str):
        self.data['secret_key'] = value.strip()
    
    @property
    def zone_id(self) -> str:
        return self.data.get('zone_id', '')
    
    @zone_id.setter
    def zone_id(self, value: str):
        self.data['zone_id'] = value.strip()
    
    @property
    def domains(self) -> List[str]:
        return self.data.get('domains', [])
    
    @domains.setter
    def domains(self, value: List[str]):
        # 过滤空值和重复项
        domains = [domain.strip() for domain in value if domain.strip()]
        self.data['domains'] = list(dict.fromkeys(domains))
    
    @property
    def ipv4_domains(self) -> List[str]:
        """获取IPv4域名列表，向后兼容：如果没有配置ipv4_domains，则使用domains"""
        ipv4_domains = self.data.get('ipv4_domains', [])
        if ipv4_domains:
            return ipv4_domains
        # 向后兼容：如果没有新的配置，使用旧的domains
        return self.data.get('domains', [])
    
    @ipv4_domains.setter
    def ipv4_domains(self, value: List[str]):
        # 过滤空值和重复项
        domains = [domain.strip() for domain in value if domain.strip()]
        self.data['ipv4_domains'] = list(dict.fromkeys(domains))
    
    @property
    def ipv6_domains(self) -> List[str]:
        """获取IPv6域名列表"""
        return self.data.get('ipv6_domains', [])
    
    @ipv6_domains.setter
    def ipv6_domains(self, value: List[str]):
        # 过滤空值和重复项
        domains = [domain.strip() for domain in value if domain.strip()]
        self.data['ipv6_domains'] = list(dict.fromkeys(domains))
    
    @property
    def wechat_webhook(self) -> str:
        return self.data.get('wechat_webhook', '')
    
    @wechat_webhook.setter
    def wechat_webhook(self, value: str):
        self.data['wechat_webhook'] = value.strip()
    
    @property
    def update_interval(self) -> int:
        return self.data.get('update_interval', 300)
    
    @update_interval.setter
    def update_interval(self, value: int):
        self.data['update_interval'] = max(60, min(86400, int(value)))  # 限制在1分钟到24小时之间
    
    @property
    def log_level(self) -> str:
        return self.data.get('log_level', 'INFO')
    
    @log_level.setter
    def log_level(self, value: str):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        self.data['log_level'] = value.upper() if value.upper() in valid_levels else 'INFO'
    
    @property
    def ipv4_enabled(self) -> bool:
        return self.data.get('ipv4_enabled', True)
    
    @ipv4_enabled.setter
    def ipv4_enabled(self, value: bool):
        self.data['ipv4_enabled'] = bool(value)
    
    @property
    def ipv6_enabled(self) -> bool:
        return self.data.get('ipv6_enabled', False)
    
    @ipv6_enabled.setter
    def ipv6_enabled(self, value: bool):
        self.data['ipv6_enabled'] = bool(value)
    
    @property
    def webhook_enabled(self) -> bool:
        return self.data.get('webhook_enabled', False)
    
    @webhook_enabled.setter
    def webhook_enabled(self, value: bool):
        self.data['webhook_enabled'] = bool(value)
    
    @property
    def webhook_url(self) -> str:
        return self.data.get('webhook_url', '')
    
    @webhook_url.setter
    def webhook_url(self, value: str):
        self.data['webhook_url'] = value.strip()
    
    @property
    def webhook_headers(self) -> dict:
        try:
            headers_str = self.data.get('webhook_headers', '{}')
            return json.loads(headers_str) if headers_str else {}
        except:
            return {}
    
    @webhook_headers.setter
    def webhook_headers(self, value: dict):
        if isinstance(value, dict):
            self.data['webhook_headers'] = json.dumps(value, ensure_ascii=False)
        else:
            self.data['webhook_headers'] = value
    
    @property
    def webhook_body_template(self) -> dict:
        try:
            body_str = self.data.get('webhook_body_template', '{}')
            return json.loads(body_str) if body_str else {}
        except:
            return {}
    
    @webhook_body_template.setter
    def webhook_body_template(self, value: dict):
        if isinstance(value, dict):
            self.data['webhook_body_template'] = json.dumps(value, ensure_ascii=False)
        else:
            self.data['webhook_body_template'] = value