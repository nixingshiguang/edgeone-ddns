#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeOne DDNS 动态域名解析系统
主应用程序入口
"""

import os
import json
import logging
import logging.handlers
from flask import Flask, render_template, request, jsonify, redirect, url_for
from jinja2 import filters
from datetime import datetime
import threading
import schedule
import time

from config import Config
from edgeone_client import EdgeOneClient
from ip_detector import IPDetector
from notification import NotificationManager
from ddns_service import DNSService

# 配置日志
def setup_logging():
    """配置日志系统，同时输出到文件和控制台"""
    
    # 创建日志目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器（带轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'ddns.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 为Flask特定日志配置
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    
    logging.info("日志系统初始化完成")

# 初始化日志
setup_logging()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'edgeone-ddns-secret-key'

# 初始化配置
config = Config()
dnsservice = DNSService(config)

# 全局变量
last_update_time = None
current_ip = None
scheduler_thread = None

# 添加模板过滤器
@app.template_filter('format_time')
def format_time(timestamp):
    """格式化时间戳"""
    if not timestamp:
        return ''
    try:
        from datetime import datetime
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

@app.template_filter('level_color')
def level_color(level):
    """根据日志级别返回颜色类"""
    colors = {
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
        'debug': 'secondary'
    }
    return colors.get(level.lower(), 'secondary')

def get_system_status():
    """获取系统状态信息"""
    global last_update_time, current_ip
    
    status = {
        'service_running': dnsservice.is_running,
        'last_update_time': last_update_time.isoformat() if last_update_time else None,
        'current_ip': current_ip,
        'config_valid': config.is_valid(),
        'total_domains': len(config.ipv4_domains or config.domains) + len(config.ipv6_domains),
        'logs': dnsservice.get_recent_logs(limit=10)
    }
    return status

@app.route('/')
def index():
    """主页 - 仪表板"""
    status = get_system_status()
    return render_template('index.html', status=status)

@app.route('/config')
def config_page():
    """配置页面"""
    return render_template('config.html', config=config.to_dict())

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """配置API接口"""
    if request.method == 'GET':
        return jsonify(config.to_dict())
    
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not all(key in data for key in ['secret_id', 'zone_id']):
            return jsonify({'error': '缺少必需的配置字段'}), 400
        
        # 更新配置
        config.secret_id = data['secret_id']
        
        # 处理secret_key：如果提交的是掩码值，则保留原值；否则更新为新值
        submitted_secret_key = data.get('secret_key', '')
        if submitted_secret_key and not submitted_secret_key.startswith('*'):
            config.secret_key = submitted_secret_key
        # 如果提交的是空值或掩码值，保持原有的secret_key不变
        
        config.zone_id = data['zone_id']
        # 保持向后兼容：如果发送了domains，则使用它
        if 'domains' in data and data['domains']:
            config.domains = data.get('domains', [])
        else:
            config.ipv4_domains = data.get('ipv4_domains', [])
            config.ipv6_domains = data.get('ipv6_domains', [])
            
        config.update_interval = int(data.get('update_interval', 300))
        config.ipv4_enabled = data.get('ipv4_enabled', True)
        config.ipv6_enabled = data.get('ipv6_enabled', False)
        
        # Webhook配置
        config.webhook_enabled = data.get('webhook_enabled', False)
        config.webhook_url = data.get('webhook_url', '')
        config.webhook_headers = data.get('webhook_headers', '{}')
        config.webhook_body_template = data.get('webhook_body_template', '{}')
        
        # 保存配置
        config.save()
        
        # 重启服务
        dnsservice.restart()
        
        return jsonify({'success': True, 'message': '配置已更新'})
    
    except Exception as e:
        logging.error(f"更新配置失败: {str(e)}")
        return jsonify({'error': f'更新配置失败: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """获取系统状态"""
    return jsonify(get_system_status())

@app.route('/api/manual_update', methods=['POST'])
def manual_update():
    """手动触发IP更新"""
    try:
        global last_update_time, current_ip
        
        # 执行IP检测和DNS更新
        ip_detector = IPDetector()
        new_ip = ip_detector.get_public_ip()
        
        if new_ip:
            # 更新全局状态
            current_ip = new_ip
            last_update_time = datetime.now()
            
            # 执行DNS更新
            result = dnsservice.update_dns_records(new_ip)
            
            return jsonify({
                'success': True,
                'message': f'IP更新完成: {new_ip}',
                'result': result
            })
        else:
            return jsonify({'error': '无法获取公网IP'}), 500
            
    except Exception as e:
        logging.error(f"手动更新失败: {str(e)}")
        return jsonify({'error': f'手动更新失败: {str(e)}'}), 500

@app.route('/api/test_notification', methods=['POST'])
def test_notification():
    """测试企业微信通知"""
    try:
        data = request.get_json()
        if data is None:
            data = {}
        
        webhook_url = data.get('webhook_url') or config.webhook_url
        webhook_headers = data.get('webhook_headers') or config.webhook_headers
        webhook_body_template = data.get('webhook_body_template') or config.webhook_body_template
        
        if not webhook_url:
            return jsonify({'error': '未配置企业微信Webhook URL'}), 400
        
        # 解析JSON配置
        try:
            headers_dict = json.loads(webhook_headers) if isinstance(webhook_headers, str) else webhook_headers
            body_template_dict = json.loads(webhook_body_template) if isinstance(webhook_body_template, str) else webhook_body_template
        except:
            headers_dict = {}
            body_template_dict = {}
        
        notification = NotificationManager(webhook_url, headers_dict, body_template_dict)
        success = notification.send_test_notification()
        
        if success:
            return jsonify({'success': True, 'message': '测试通知发送成功'})
        else:
            return jsonify({'error': '测试通知发送失败'}), 500
            
    except Exception as e:
        logging.error(f"测试通知失败: {str(e)}")
        return jsonify({'error': f'测试通知失败: {str(e)}'}), 500

@app.route('/api/test_connectivity', methods=['POST'])
def test_connectivity():
    """测试连接性"""
    try:
        data = request.get_json()
        if data is None:
            data = {}
        
        # 如果提供了临时配置，使用临时配置进行测试
        if data and data.get('secret_id') and data.get('zone_id'):
            temp_config = Config()
            temp_config.secret_id = data['secret_id']
            temp_config.zone_id = data['zone_id']
            
            # 处理secret_key：如果提供了且不是掩码，则使用提供的值；否则使用当前配置的值
            submitted_secret_key = data.get('secret_key', '')
            if submitted_secret_key and not submitted_secret_key.startswith('*'):
                temp_config.secret_key = submitted_secret_key
            else:
                # 使用现有配置的secret_key
                temp_config.secret_key = config.secret_key
                
            temp_config.wechat_webhook = data.get('wechat_webhook', config.wechat_webhook)
            temp_service = DNSService(temp_config)
            result = temp_service.test_connectivity()
        else:
            result = dnsservice.test_connectivity()
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"连接测试失败: {str(e)}")
        return jsonify({'success': False, 'message': f'连接测试失败: {str(e)}'}), 500

@app.route('/api/logs/clear', methods=['DELETE'])
def clear_logs():
    """清空日志"""
    try:
        dnsservice.update_history.clear()
        dnsservice._add_log("info", "日志已清空")
        return jsonify({'success': True, 'message': '日志已清空'})
    except Exception as e:
        logging.error(f"清空日志失败: {str(e)}")
        return jsonify({'error': f'清空日志失败: {str(e)}'}), 500

@app.route('/logs')
def logs_page():
    """日志页面"""
    logs = dnsservice.get_recent_logs(limit=100)
    return render_template('logs.html', logs=logs)

def run_scheduler():
    """运行定时任务调度器"""
    while True:
        schedule.run_pending()
        time.sleep(60)

def init_scheduler():
    """初始化定时任务"""
    global scheduler_thread
    
    # 清除所有现有任务
    schedule.clear()
    
    # 添加定时更新任务
    schedule.every(config.update_interval).seconds.do(
        lambda: dnsservice.check_and_update_ip()
    )
    
    # 启动调度器线程
    if not scheduler_thread or not scheduler_thread.is_alive():
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logging.info("定时任务调度器已启动")

if __name__ == '__main__':
    # 加载配置
    config.load()
    
    # 初始化定时任务
    init_scheduler()
    
    # 启动DNSService
    dnsservice.start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=4646, debug=False, threaded=True)