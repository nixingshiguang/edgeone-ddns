/**
 * EdgeOne DDNS - 主JavaScript文件
 */

// 全局变量
window.EdgeOneDDNS = {
    config: {},
    status: {},
    timer: null
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 初始化工具提示
    initializeTooltips();
    
    // 设置定时刷新
    if (window.location.pathname === '/') {
        startAutoRefresh();
    }
    
    // 绑定全局事件
    bindGlobalEvents();
    
    console.log('EdgeOne DDNS 应用初始化完成');
}

// 初始化Bootstrap工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 绑定全局事件
function bindGlobalEvents() {
    // 监听页面可见性变化
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            if (window.location.pathname === '/') {
                startAutoRefresh();
            }
        }
    });
    
    // 监听模态框关闭事件
    document.addEventListener('hidden.bs.modal', function(e) {
        // 清理模态框内容
        const modal = e.target;
        if (modal.id === 'messageModal') {
            setTimeout(() => {
                const content = modal.querySelector('#modalMessage');
                if (content) {
                    content.innerHTML = '';
                }
            }, 300);
        }
    });
}

// 启动自动刷新
function startAutoRefresh() {
    stopAutoRefresh();
    window.EdgeOneDDNS.timer = setInterval(function() {
        updateStatus();
    }, 30000); // 30秒刷新一次
}

// 停止自动刷新
function stopAutoRefresh() {
    if (window.EdgeOneDDNS.timer) {
        clearInterval(window.EdgeOneDDNS.timer);
        window.EdgeOneDDNS.timer = null;
    }
}

// 更新状态信息
function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            window.EdgeOneDDNS.status = data;
            updateStatusDisplay(data);
        })
        .catch(error => {
            console.error('更新状态失败:', error);
        });
}

// 更新状态显示
function updateStatusDisplay(status) {
    // 更新服务状态指示器
    const statusIndicators = document.querySelectorAll('.status-indicator');
    statusIndicators.forEach(indicator => {
        if (status.service_running) {
            indicator.classList.remove('status-stopped');
            indicator.classList.add('status-running');
        } else {
            indicator.classList.remove('status-running');
            indicator.classList.add('status-stopped');
        }
    });
    
    // 更新导航栏状态文本
    const navbarText = document.querySelector('.navbar-text');
    if (navbarText) {
        const icon = navbarText.querySelector('i');
        if (icon) {
            icon.className = `bi bi-circle-fill ${status.service_running ? 'text-success' : 'text-danger'}`;
        }
        const text = navbarText.lastChild;
        if (text) {
            text.textContent = `服务${status.service_running ? '运行中' : '已停止'}`;
        }
    }
}

// 工具函数
const Utils = {
    // 格式化时间
    formatTime: function(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },
    
    // 获取级别颜色
    getLevelColor: function(level) {
        const colors = {
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'debug': 'secondary'
        };
        return colors[level.toLowerCase()] || 'secondary';
    },
    
    // 显示消息提示
    showMessage: function(message, type, duration = 3000) {
        const alertId = 'alert-' + Date.now();
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                 style="z-index: 9999; min-width: 300px;" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // 自动消失
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }
        }, duration);
    },
    
    // 显示加载状态
    showLoading: function(message = '正在处理，请稍候...') {
        const modal = document.getElementById('messageModal');
        if (modal) {
            const content = modal.querySelector('#modalMessage');
            if (content) {
                content.innerHTML = `
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">${message}</p>
                    </div>
                `;
            }
            new bootstrap.Modal(modal).show();
        }
    },
    
    // 隐藏加载状态
    hideLoading: function() {
        const modal = document.getElementById('messageModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    },
    
    // 显示模态框
    showModal: function(title, content, size = 'md') {
        const modal = document.getElementById('messageModal');
        if (modal) {
            // 更新模态框大小
            const dialog = modal.querySelector('.modal-dialog');
            dialog.className = `modal-dialog modal-${size}`;
            
            // 更新标题和内容
            const titleElement = modal.querySelector('.modal-title');
            const contentElement = modal.querySelector('#modalMessage');
            
            if (titleElement) titleElement.textContent = title;
            if (contentElement) contentElement.innerHTML = content;
            
            new bootstrap.Modal(modal).show();
        }
    },
    
    // 确认对话框
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // 复制到剪贴板
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            Utils.showMessage('已复制到剪贴板', 'success', 2000);
        }).catch(() => {
            // 降级方案
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            Utils.showMessage('已复制到剪贴板', 'success', 2000);
        });
    }
};

// API工具类
const API = {
    // GET请求
    get: function(url) {
        return fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },
    
    // POST请求
    post: function(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },
    
    // DELETE请求
    delete: function(url) {
        return fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    }
};

// 导出到全局
window.Utils = Utils;
window.API = API;

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});