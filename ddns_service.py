#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDNS服务核心模块
"""

import logging
import threading
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config import Config
from edgeone_client import EdgeOneClient
from ip_detector import IPDetector
from notification import NotificationManager

class DNSService:
    """DDNS服务核心类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.is_running = False
        self.last_check_time: Optional[datetime] = None
        self.last_ip: Optional[str] = None
        self.update_history: List[Dict] = []
        self.max_history = 100
        
        # 初始化组件
        self.edgeone_client: Optional[EdgeOneClient] = None
        self.ip_detector = IPDetector()
        self.notification_manager = NotificationManager()
        
        # 线程锁
        self._lock = threading.Lock()
    
    def _init_clients(self) -> bool:
        """初始化API客户端"""
        try:
            if not self.config.is_valid():
                logging.error("配置无效，无法初始化客户端")
                return False
            
            self.edgeone_client = EdgeOneClient(
                self.config.secret_id,
                self.config.secret_key
            )
            
            # 设置新的Webhook通知配置
            if self.config.webhook_enabled:
                self.notification_manager.set_webhook_config(
                    self.config.webhook_url,
                    self.config.webhook_headers,
                    self.config.webhook_body_template
                )
            
            logging.info("API客户端初始化成功")
            return True
            
        except Exception as e:
            logging.error(f"初始化客户端失败: {str(e)}")
            return False
    
    def start(self) -> bool:
        """启动DDNS服务"""
        with self._lock:
            if self.is_running:
                logging.warning("DDNS服务已在运行")
                return True
            
            if not self._init_clients():
                logging.error("DDNS服务启动失败")
                return False
            
            self.is_running = True
            
            # 获取启用的域名列表
            all_domains = []
            if self.config.ipv4_enabled:
                all_domains.extend(self.config.ipv4_domains)
            if self.config.ipv6_enabled:
                all_domains.extend(self.config.ipv6_domains)
            
            # 发送启动通知
            if self.config.webhook_enabled and self.config.webhook_url and all_domains:
                self.notification_manager.send_startup_notification(all_domains)
            
            # 执行首次检查
            self.check_and_update_ip()
            
            logging.info("DDNS服务启动成功")
            return True
    
    def stop(self) -> bool:
        """停止DDNS服务"""
        with self._lock:
            self.is_running = False
            logging.info("DDNS服务已停止")
            return True
    
    def restart(self) -> bool:
        """重启DDNS服务"""
        self.stop()
        return self.start()
    
    def check_and_update_ip(self) -> Dict:
        """检查并更新IP地址"""
        if not self.is_running:
            return {"success": False, "message": "DDNS服务未运行"}
        
        if not self.edgeone_client:
            return {"success": False, "message": "EdgeOne客户端未初始化"}
        
        # 检查是否启用了任何IP类型
        if not self.config.ipv4_enabled and not self.config.ipv6_enabled:
            self._add_log("info", "未启用任何IP类型，跳过DDNS任务")
            return {
                "success": True,
                "message": "未启用任何IP类型，不执行DDNS任务",
                "action": "disabled",
                "ip_info": {},
                "results": []
            }
        
        try:
            # 获取所有IP信息
            ip_info = self.ip_detector.get_all_ips(
                self.config.ipv4_enabled, 
                self.config.ipv6_enabled
            )
            
            results = []
            total_updates = 0
            success_updates = 0
            
            # 处理IPv4更新
            if self.config.ipv4_enabled:
                ipv4_address = ip_info.get('ipv4')
                if ipv4_address:
                    ipv4_results = self.update_dns_records(ipv4_address, 'A')
                    results.extend(ipv4_results)
                    total_updates += len(ipv4_results)
                    success_updates += sum(1 for r in ipv4_results if r.get('success'))
                else:
                    self._add_log("error", "获取IPv4地址失败")
            
            # 处理IPv6更新
            if self.config.ipv6_enabled:
                ipv6_address = ip_info.get('ipv6')
                if ipv6_address:
                    ipv6_results = self.update_dns_records(ipv6_address, 'AAAA')
                    results.extend(ipv6_results)
                    total_updates += len(ipv6_results)
                    success_updates += sum(1 for r in ipv6_results if r.get('success'))
                else:
                    self._add_log("error", "获取IPv6地址失败")
            
            if not results:
                return {"success": False, "message": "没有可更新的IP地址"}
            
            self.last_check_time = datetime.now()
            
            # 更新last_ip（用于向后兼容，保存最后一次的IPv4地址）
            if self.config.ipv4_enabled:
                self.last_ip = ip_info.get('ipv4')
            
            self._add_log("info", f"IP更新完成, 成功: {success_updates}/{total_updates}")
            
            # 发送通知
            if self.config.webhook_enabled and self.config.webhook_url:
                if len(results) > 1:
                    self.notification_manager.send_batch_update_notification(results)
                elif results:
                    result = results[0]
                    self.notification_manager.send_ip_update_notification(
                        result.get('domain', ''),
                        result.get('old_ip'),
                        result.get('ip_address'),
                        result.get('action', 'updated')
                    )
            
            return {
                "success": success_updates == total_updates,
                "message": f"IP更新完成, 成功: {success_updates}/{total_updates}",
                "ip_info": ip_info,
                "results": results
            }
            
        except Exception as e:
            error_msg = f"检查更新IP失败: {str(e)}"
            self._add_log("error", error_msg)
            
            # 发送错误通知
            if self.config.webhook_enabled and self.config.webhook_url:
                self.notification_manager.send_error_notification(error_msg)
            
            return {"success": False, "message": error_msg}
    
    def update_dns_records(self, ip_address: str, record_type: str = 'A') -> List[Dict]:
        """更新所有域名的DNS记录"""
        if not self.edgeone_client:
            return []
        
        # 根据记录类型选择域名列表
        if record_type == 'A':
            domains = self.config.ipv4_domains
        elif record_type == 'AAAA':
            domains = self.config.ipv6_domains
        else:
            return []
        
        if not domains:
            return []
        
        results = []
        
        for domain in domains:
            if record_type == 'A':
                result = self.edgeone_client.update_or_create_a_record(
                    self.config.zone_id,
                    domain,
                    ip_address
                )
            elif record_type == 'AAAA':
                result = self.edgeone_client.update_or_create_aaaa_record(
                    self.config.zone_id,
                    domain,
                    ip_address
                )
            else:
                result = {
                    "success": False,
                    "message": f"不支持的记录类型: {record_type}"
                }
            
            # 添加域名信息到结果
            result['domain'] = domain
            result['ip_address'] = ip_address
            result['record_type'] = record_type
            result['timestamp'] = datetime.now().isoformat()
            
            # 记录日志
            if result['success']:
                self._add_log("info", result['message'])
            else:
                self._add_log("error", result['message'])
            
            results.append(result)
        
        return results
    
    def get_status(self) -> Dict:
        """获取服务状态"""
        # 计算域名数量
        ipv4_count = len(self.config.ipv4_domains) if self.config.ipv4_domains else 0
        ipv6_count = len(self.config.ipv6_domains) if self.config.ipv6_domains else 0
        total_count = ipv4_count + ipv6_count
        
        return {
            "is_running": self.is_running,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "last_ip": self.last_ip,
            "config_valid": self.config.is_valid(),
            "ipv4_domains": ipv4_count,
            "ipv6_domains": ipv6_count,
            "total_domains": total_count,
            "update_interval": self.config.update_interval
        }
    
    def get_recent_logs(self, limit: int = 50, include_file_logs: bool = True) -> List[Dict]:
        """获取最近的日志记录"""
        logs = []
        
        # 如果启用文件日志，从日志文件读取更多日志
        if include_file_logs:
            file_logs = self._get_logs_from_file(limit - len(self.update_history))
            logs.extend(file_logs)
        
        # 添加内存中的最新日志
        logs.extend(self.update_history)
        
        # 按时间排序并限制数量
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return logs[:limit] if logs else []
    
    def _get_logs_from_file(self, limit: int) -> List[Dict]:
        """从日志文件读取最近的日志记录"""
        try:
            import os
            log_file = os.path.join('logs', 'ddns.log')
            
            if not os.path.exists(log_file):
                return []
            
            file_logs = []
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 只读取最后几行
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            for line in recent_lines:
                try:
                    # 解析日志行格式: timestamp - name - level - message
                    parts = line.strip().split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        name = parts[1]
                        level = parts[2]
                        message = parts[3]
                        
                        # 转换时间格式
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f').isoformat()
                        except:
                            timestamp = timestamp_str
                        
                        # 过滤掉一些不重要的日志
                        if any(keyword in message.lower() for keyword in ['127.0.0.1', 'GET /', 'POST /api/', '200 OK']):
                            continue
                            
                        file_logs.append({
                            'timestamp': timestamp,
                            'level': level.upper(),
                            'message': f'[{name}] {message}'
                        })
                except Exception as e:
                    # 如果解析失败，跳过这行
                    continue
            
            return file_logs[-limit:] if file_logs else []
            
        except Exception as e:
            logging.error(f"读取日志文件失败: {e}")
            return []
    
    def _add_log(self, level: str, message: str):
        """添加日志记录"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        self.update_history.append(log_entry)
        
        # 限制历史记录数量
        if len(self.update_history) > self.max_history:
            self.update_history = self.update_history[-self.max_history:]
        
        # 记录到系统日志
        log_method = getattr(logging, level.lower(), logging.info)
        log_method(message)
    
    def test_connectivity(self) -> Dict:
        """测试连接性"""
        try:
            if not self._init_clients():
                return {"success": False, "message": "初始化客户端失败"}
            
            # 测试EdgeOne API连接
            test_results = {}
            
            # 1. 测试获取公网IP
            ipv4_ip = None
            ipv6_ip = None
            
            if self.config.ipv4_enabled:
                ipv4_ip = self.ip_detector.get_ipv4()
                test_results['ipv4'] = {
                    "success": bool(ipv4_ip),
                    "value": ipv4_ip or "获取失败"
                }
            
            if self.config.ipv6_enabled:
                ipv6_ip = self.ip_detector.get_ipv6()
                test_results['ipv6'] = {
                    "success": bool(ipv6_ip),
                    "value": ipv6_ip or "获取失败"
                }
            
            # 保持向后兼容性
            public_ip = ipv4_ip
            test_results['public_ip'] = {
                "success": bool(public_ip),
                "value": public_ip or "获取失败"
            }
            
            # 2. 测试EdgeOne API
            try:
                response = self.edgeone_client.describe_dns_records(self.config.zone_id)
                test_results['edgeone_api'] = {
                    "success": True,
                    "value": "连接正常"
                }
            except Exception as e:
                test_results['edgeone_api'] = {
                    "success": False,
                    "value": f"连接失败: {str(e)}"
                }
            
            # 3. 测试Webhook通知
            try:
                if self.config.webhook_enabled and self.config.webhook_url:
                    webhook_success = self.notification_manager.send_test_notification()
                    test_results['webhook'] = {
                        "success": webhook_success,
                        "value": "发送成功" if webhook_success else "发送失败"
                    }
                else:
                    test_results['webhook'] = {
                        "success": None,
                        "value": "未配置"
                    }
            except Exception as e:
                test_results['webhook'] = {
                    "success": False,
                    "value": f"测试失败: {str(e)}"
                }
            
            # 4. 查找现有DNS记录
            all_domains = []
            if self.config.ipv4_domains:
                all_domains.extend(self.config.ipv4_domains)
            if self.config.ipv6_domains:
                all_domains.extend(self.config.ipv6_domains)
                
            if all_domains:
                domain_test_results = []
                for domain in all_domains[:3]:  # 只测试前3个域名
                    record = self.edgeone_client.find_a_record(self.config.zone_id, domain)
                    domain_test_results.append({
                        "domain": domain,
                        "exists": record is not None,
                        "current_ip": record.get("Content") if record else None
                    })
                test_results['dns_records'] = domain_test_results
            
            return {
                "success": True,
                "message": "连接性测试完成",
                "results": test_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"连接性测试失败: {str(e)}"
            }