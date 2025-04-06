# Clash 配置合并工具

这是一个用于合并多个Clash配置文件的工具，它可以获取多个配置源，合并节点，测试延迟，并生成优化后的配置文件。

## 特性

- 支持从多个URL和本地文件加载配置
- 自动合并和去重代理节点
- 节点延迟测试和排序
- Web界面进行配置和管理
- 支持中断任务并保存中间结果

## 云端部署

### Replit平台部署（免费）

1. 注册[Replit](https://replit.com/)账户
2. 点击"+ Create Repl"创建新项目
3. 选择"Import from GitHub"
4. 输入仓库地址并导入
5. 导入完成后点击"Run"按钮启动应用

#### 环境变量设置
在Replit的"Secrets"工具中添加以下环境变量:
- `USE_CLOUD_CONFIG`: true
- `URL_SOURCE_FILE`: config_urls.txt
- `PROXY_ENABLE`: true/false (取决于是否需要代理)
- `PROXY_ADDRESS`: 你的HTTP代理地址(如果启用)

#### 可能遇到的问题和解决方案

1. **依赖安装失败**
   - 问题: PyYAML, aiohttp等包安装失败
   - 解决方案: 在Replit的Shell中手动运行
     ```
     pip install flask flask-cors aiohttp asyncio pyyaml requests python-dotenv rich gunicorn
     ```

2. **应用启动失败**
   - 问题: ModuleNotFoundError: No module named 'xxx'
   - 解决方案: 运行以下命令安装缺失的包
     ```
     pip install xxx
     ```

3. **应用无法访问**
   - 问题: 应用启动后无法访问
   - 解决方案: 确保Replit的"Webview"标签已打开，或使用提供的URL访问

4. **应用休眠**
   - 问题: Replit免费版会让应用在不活跃一段时间后休眠
   - 解决方案: 使用[UptimeRobot](https://uptimerobot.com/)等服务定期ping应用URL

## 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python webui.py
```

### 配置

编辑`config.yaml`文件或设置环境变量来配置应用。

### 配置URL源

你可以通过以下两种方式配置Clash配置源URL:

1. **使用TXT文件 (推荐)**: 
   - 创建一个名为`config_urls.txt`的文件
   - 每行放置一个URL
   - 可以使用#添加注释行
   - 设置环境变量`URL_SOURCE_FILE`指向这个文件

2. **直接在配置文件中设置**:
   - 在`config.yaml`中的`yaml_urls`列表中添加URL

## 防止应用休眠（重要）

Replit免费版会让应用在一段时间不活跃后休眠（通常是1小时），导致应用无法访问。以下是几种防止应用休眠的方法：

### 方法1：使用UptimeRobot（推荐）

1. 注册[UptimeRobot](https://uptimerobot.com/)免费账号
2. 添加新的监控器：
   - 监控类型：HTTP(s)
   - 友好名称：任意（例如"Clash配置合并工具"）
   - URL：你的Replit应用URL（例如 https://clash-config-merger.用户名.repl.co）
   - 监控间隔：设置为5分钟（免费版最短间隔）
3. 点击"Create Monitor"创建监控
4. UptimeRobot将每5分钟访问一次你的应用，保持它处于活跃状态

### 方法2：添加自我ping脚本

1. 在项目中创建`ping.py`文件：
```python
import time
import requests
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 应用URL - 替换为你的实际URL
APP_URL = "https://你的应用名.用户名.repl.co"

logger.info("启动自我ping服务...")

while True:
    try:
        response = requests.get(APP_URL)
        logger.info(f"Ping结果: {response.status_code}")
    except Exception as e:
        logger.error(f"Ping失败: {str(e)}")
    
    # 每15分钟ping一次
    time.sleep(900)
```

2. 修改`.replit`文件以同时运行主应用和ping脚本：
```
run = "python webui.py & python ping.py"
```

### 方法3：使用其他免费服务

还可以使用其他免费的监控服务来定期访问你的应用：

- [Cron-Job.org](https://cron-job.org)：提供免费的定时任务服务
- [Kaffeine](https://kaffeine.herokuapp.com/)：专为保持应用唤醒设计（注册后使用）
- [New Relic](https://newrelic.com/)：提供免费的基础监控

### 方法4：定期手动访问

如果只是个人使用，最简单的方法是：
- 将应用URL添加到浏览器书签
- 定期（至少每天一次）访问应用
- 或在手机上设置定时提醒访问应用

## 其他维护技巧

1. **定期登录Replit**：至少每14天登录一次Replit账户，否则项目可能会被归档
2. **创建备份**：定期导出生成的配置文件，以防数据丢失
3. **安装Replit移动应用**：方便随时检查和重启应用
4. **关注资源限制**：Replit免费版有CPU和内存限制，避免运行过于复杂的操作

## 许可证

MIT
