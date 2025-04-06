/**
 * Clash配置合并工具 - 主JavaScript文件
 */

// 全局工具函数
const ClashTools = {
    // 格式化日期时间
    formatDateTime: function(dateStr) {
        if (!dateStr) return '未知';
        const date = new Date(dateStr);
        return date.toLocaleString('zh-CN');
    },
    
    // 格式化文件大小
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 显示提示消息
    showToast: function(message, type = 'info') {
        // 检查是否已存在toast容器
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // 创建toast元素
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        // 显示toast
        const toast = new bootstrap.Toast(toastEl, {
            delay: 3000
        });
        toast.show();
        
        // toast消失后删除元素
        toastEl.addEventListener('hidden.bs.toast', function () {
            toastEl.remove();
        });
    },
    
    // 确认对话框
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
};

// 在页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 如果有任何基于全局作用域的功能，可以在这里初始化
    console.log('Clash配置合并工具 - Web界面已加载');
}); 