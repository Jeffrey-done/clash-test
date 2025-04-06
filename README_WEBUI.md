# Clash配置合并工具 WebUI

这是Clash配置合并工具的Web界面，提供了直观的图形界面来管理和优化Clash代理配置。

## 功能特点

- **直观的配置管理**：通过Web界面轻松管理配置源、设置HTTP代理和调整延迟测试参数
- **节点管理**：查看所有代理节点，支持搜索、排序和详细信息查看
- **实时状态监控**：可视化显示任务进度和状态更新
- **配置文件查看**：在线查看和下载生成的Clash配置文件
- **运行日志**：实时查看处理日志，方便排查问题

## 安装与使用

### 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动Web服务：
```bash
python webui.py
```

3. 在浏览器中访问：`http://localhost:5000`

### 生产环境部署

1. 使用Gunicorn启动：
```bash
gunicorn -c gunicorn_config.py webui:app
```

2. 或者使用Docker（需要先创建Dockerfile）：
```bash
docker build -t clash-config-merger .
docker run -p 8080:8080 clash-config-merger
```

## 部署到Cloudflare Pages

本项目支持一键部署到Cloudflare Pages，结合GitHub Actions实现自动化部署流程。

### 步骤

1. Fork本仓库到你的GitHub账户

2. 在GitHub仓库设置中添加以下Secrets：
   - `CLOUDFLARE_API_TOKEN`：你的Cloudflare API令牌
   - `CLOUDFLARE_ACCOUNT_ID`：你的Cloudflare账户ID

3. 推送代码到main分支，GitHub Actions将自动部署到Cloudflare Pages

4. 访问Cloudflare Pages生成的网址使用Web界面

## 界面指南

### 首页

- **系统状态**：显示当前任务状态、进度和上次运行时间
- **配置信息**：显示当前配置摘要
- **输出文件**：列出生成的所有配置文件，支持查看和下载
- **最近日志**：显示最近的运行日志

### 节点管理

- 查看所有可用的代理节点
- 搜索特定节点
- 按名称、类型或延迟排序
- 查看节点详细信息

### 配置设置

- 管理YAML URL和本地文件源
- 调整延迟测试参数
- 配置HTTP代理
- 自定义输出设置

### 运行日志

- 查看完整的任务运行日志
- 实时刷新日志内容

## 高级使用技巧

1. **定时任务**：结合系统的cron或计划任务，定期运行`python run_task.py`更新配置

2. **API访问**：
   - `/api/status`：获取当前任务状态
   - `/api/config`：获取或更新配置
   - `/api/run`：触发任务运行
   - `/api/logs`：获取运行日志
   - `/api/files`：获取文件列表

3. **移动设备访问**：WebUI采用响应式设计，支持移动设备访问

## 故障排除

- **无法连接到GitHub**：检查HTTP代理设置是否正确
- **任务执行超时**：尝试减少源URL数量或增加超时时间
- **节点延迟测试失败**：确保网络连接稳定，可能需要调整并发数和重试次数

## 贡献

欢迎提交Pull Request或Issue来改进项目！ 