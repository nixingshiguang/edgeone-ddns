#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知管理模块 - 自定义Webhook通知
"""

import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, List
from string import Template

class NotificationManager:
    """自定义Webhook通知管理器"""
    
    def __init__(self, webhook_url: str = "", webhook_headers: dict = None, webhook_body_template: dict = None):
        self.webhook_url = webhook_url
        self.webhook_headers = webhook_headers or {}
        self.webhook_body_template = webhook_body_template or {}
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'EdgeOne-DDNS-Notifier/2.0',
            'Content-Type': 'application/json'
        })
    
    def set_webhook_config(self, webhook_url: str, webhook_headers: dict = None, webhook_body_template: dict = None):
        """设置Webhook配置"""
        self.webhook_url = webhook_url
        self.webhook_headers = webhook_headers or {}
        self.webhook_body_template = webhook_body_template or {}
    
    def _format_variables(self, context: Dict) -> Dict:
        """格式化变量，用于模板替换"""
        # 基础变量
        variables = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp_iso': datetime.now().isoformat(),
            'timestamp_unix': int(datetime.now().timestamp()),
        }
        
        # 添加上下文变量
        variables.update(context)
        
        # 格式化复杂变量为JSON字符串
        # 创建副本避免修改原始字典
        variables_copy = variables.copy()
        for key, value in variables_copy.items():
            if isinstance(value, (dict, list)):
                variables[f"{key}_json"] = json.dumps(value, ensure_ascii=False, indent=2)
                variables[f"{key}_string"] = json.dumps(value, ensure_ascii=False)
        
        return variables
    
    def _substitute_template(self, template: any, variables: Dict) -> any:
        """递归替换模板中的变量"""
        if isinstance(template, str):
            try:
                # 使用字符串模板替换变量
                t = Template(template)
                return t.safe_substitute(variables)
            except:
                return template
        elif isinstance(template, dict):
            return {k: self._substitute_template(v, variables) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._substitute_template(item, variables) for item in template]
        else:
            return template
    
    def _send_webhook(self, context: Dict) -> bool:
        """发送Webhook通知"""
        if not self.webhook_url:
            logging.warning("未配置Webhook URL")
            return False
        
        try:
            # 格式化变量
            variables = self._format_variables(context)
            
            # 准备请求头
            headers = self._substitute_template(self.webhook_headers, variables)
            
            # 准备请求体
            body = self._substitute_template(self.webhook_body_template, variables)
            
            # 合并默认请求头和自定义请求头
            final_headers = {
                'User-Agent': 'EdgeOne-DDNS-Notifier/2.0',
                'Content-Type': 'application/json'
            }
            final_headers.update(headers)
            
            logging.debug(f"发送Webhook通知到: {self.webhook_url}")
            logging.debug(f"请求头: {final_headers}")
            logging.debug(f"请求体: {json.dumps(body, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(
                self.webhook_url,
                json=body,
                headers=final_headers,
                timeout=15
            )
            response.raise_for_status()
            
            logging.info("Webhook通知发送成功")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Webhook通知请求失败: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Webhook通知发送异常: {str(e)}")
            return False
    
    def send_ip_update_notification(self, domain: str, old_ip: Optional[str], new_ip: str, action: str) -> bool:
        """发送IP更新通知"""
        context = {
            'type': 'ip_update',
            'domain': domain,
            'old_ip': old_ip,
            'new_ip': new_ip,
            'action': action,
            'record_type': 'A' if '.' in new_ip else 'AAAA',
            'title': f"DNS记录{action}" if action != 'created' else "DNS记录创建",
            'message': f"域名 {domain} 的DNS记录已{action}: {new_ip}"
        }
        
        return self._send_webhook(context)
    
    def send_batch_update_notification(self, results: List[Dict]) -> bool:
        """发送批量更新结果通知"""
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        context = {
            'type': 'batch_update',
            'results': results,
            'success_count': success_count,
            'total_count': total_count,
            'success_rate': f"{success_count}/{total_count}",
            'is_partial_success': success_count > 0 and success_count < total_count,
            'is_all_success': success_count == total_count,
            'is_all_failed': success_count == 0,
            'title': 'DNS批量更新结果',
            'message': f'批量更新完成: {success_count}/{total_count} 成功'
        }
        
        return self._send_webhook(context)
    
    def send_system_alert(self, title: str, content: str, level: str = "warning") -> bool:
        """发送系统告警"""
        context = {
            'type': 'system_alert',
            'title': title,
            'content': content,
            'level': level,
            'message': f"[{level.upper()}] {title}: {content}",
            'icon': {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'success': '✅'
            }.get(level, 'ℹ️')
        }
        
        return self._send_webhook(context)
    
    def send_test_notification(self) -> bool:
        """发送测试通知"""
        context = {
            'type': 'test',
            'title': '测试通知',
            'message': '这是一条测试消息，用于验证通知功能是否正常工作',
            'status': 'success',
            'description': 'EdgeOne DDNS Webhook通知连接正常'
        }
        
        return self._send_webhook(context)
    
    def send_startup_notification(self, domains: List[str]) -> bool:
        """发送服务启动通知"""
        context = {
            'type': 'startup',
            'title': 'EdgeOne DDNS 服务启动',
            'domains': domains,
            'domain_count': len(domains),
            'message': f'服务已启动，监控 {len(domains)} 个域名',
            'status': 'running'
        }
        
        return self._send_webhook(context)
    
    def send_error_notification(self, error_message: str, context: Optional[Dict] = None) -> bool:
        """发送错误通知"""
        error_context = {
            'type': 'error',
            'title': '系统错误',
            'error_message': error_message,
            'message': f'系统错误: {error_message}',
            'level': 'error',
            'status': 'error'
        }
        
        if context:
            error_context.update(context)
        
        return self._send_webhook(error_context)
    
    def send_custom_notification(self, context: Dict) -> bool:
        """发送自定义通知"""
        if 'type' not in context:
            context['type'] = 'custom'
        if 'title' not in context:
            context['title'] = '自定义通知'
        
        return self._send_webhook(context)


# 预定义的Webhook模板
WEBHOOK_TEMPLATES = {
    # 钉钉机器人模板
    'dingtalk': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'msgtype': 'text',
            'text': {
                'content': 'EdgeOne DDNS\n${title}\n${message}\n时间: ${timestamp}'
            }
        }
    },
    
    # Slack Webhook模板
    'slack': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'text': '${title}',
            'blocks': [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': '${title}'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '${message}'
                    }
                },
                {
                    'type': 'context',
                    'elements': [
                        {
                            'type': 'mrkdwn',
                            'text': '时间: ${timestamp}'
                        }
                    ]
                }
            ]
        }
    },
    
    # Discord Webhook模板
    'discord': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'username': 'EdgeOne DDNS',
            'avatar_url': 'https://via.placeholder.com/64',
            'embeds': [
                {
                    'title': '${title}',
                    'description': '${message}',
                    'color': 5814783,
                    'timestamp': '${timestamp_iso}'
                }
            ]
        }
    },
    
    # 企业微信机器人模板
    'wechat': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'msgtype': 'text',
            'text': {
                'content': 'EdgeOne DDNS\n${title}\n${message}\n时间: ${timestamp}'
            }
        }
    },
    
    # 企业微信Markdown模板
    'wechat_markdown': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'msgtype': 'markdown',
            'markdown': {
                'content': '## ${title}\n\n${message}\n\n时间: ${timestamp}'
            }
        }
    },
    
    # 通用JSON模板
    'generic': {
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'service': 'EdgeOne DDNS',
            'type': '${type}',
            'title': '${title}',
            'message': '${message}',
            'timestamp': '${timestamp}',
            'data': {
                'domain': '${domain}',
                'old_ip': '${old_ip}',
                'new_ip': '${new_ip}',
                'action': '${action}'
            }
        }
    }
}