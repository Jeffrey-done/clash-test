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

Replit免费版会让应用在一段时间不活跃后休眠（通常是1小时），导致应用无法访问。本项目已内置防休眠功能，但以下是几种确保应用始终在线的方法：

### 内置防休眠功能（推荐）

**最新版本已内置自动防休眠功能，无需额外设置！**

- 应用启动时会自动检测是否在Replit环境中运行
- 如果是Replit环境，会启动后台防休眠线程
- 该线程会定期ping应用自身，防止Replit休眠
- 默认每15分钟ping一次，可通过环境变量`PING_INTERVAL`调整

您可以在日志中看到类似的消息，确认防休眠功能已启动：
```
INFO - 已启动Replit防休眠服务
INFO - 防休眠服务已启动，目标URL: https://您的应用.repl.co, 间隔: 900秒
```

### 额外保障措施

虽然内置功能通常已足够，但为了万无一失，您也可以采用以下额外措施：

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

## 自定义域名设置

Replit免费版支持绑定自定义域名，可以使用你自己的域名代替默认的`.replit.app`域名，让应用看起来更专业。

### 步骤1：准备一个域名

首先，你需要拥有一个域名。可以从以下域名注册商购买：
- [Namecheap](https://www.namecheap.com/)
- [GoDaddy](https://www.godaddy.com/)
- [阿里云](https://wanwang.aliyun.com/)
- [腾讯云](https://dnspod.cloud.tencent.com/)

### 步骤2：在Replit中配置自定义域名

1. 打开你的Repl项目
2. 点击顶部的项目名称旁边的"三点"菜单
3. 选择"Settings"（设置）
4. 在左侧菜单中，找到并点击"Custom domains"（自定义域名）
5. 点击"Add a custom domain"（添加自定义域名）按钮
6. 输入你的域名（例如：`clash.example.com`）
7. Replit会显示必要的DNS记录信息

### 步骤3：设置DNS记录

登录到你的域名管理面板（域名注册商提供），添加Replit提供的DNS记录：

**方法1：使用CNAME记录（推荐）**
- 类型：`CNAME`
- 主机名/Name：通常是子域名部分（如`clash`）
- 目标/Value：Replit提供的值（通常形如`项目名.用户名.repl.co`）
- TTL：可使用默认值（如3600或自动）

**方法2：使用A记录**
- 类型：`A`
- 主机名/Name：通常是子域名部分（如`clash`）
- 目标/Value：Replit提供的IP地址
- TTL：可使用默认值

### 步骤4：验证并激活

1. 在Replit的"Custom domains"页面，点击"Verify"（验证）按钮
2. DNS更改可能需要几分钟到几小时不等才能生效
3. 验证成功后，你将看到状态变为"Active"（激活）
4. 现在可以使用你的自定义域名访问应用（如`https://clash.example.com`）

### 使用自定义域名的优势

1. **专业形象**：自定义域名让应用看起来更加专业
2. **易于记忆**：比默认的`.replit.app`域名更好记
3. **更好的用户体验**：用户不用记住复杂的Replit默认URL
4. **避免休眠问题**：通过自定义域名访问应用，可以确保UptimeRobot等服务正确找到你的应用

### 注意事项

- 自定义域名需要域名本身的年费，但Replit不会额外收费
- 如果使用二级域名（如`clash.example.com`），必须是你控制的域名
- Replit会自动提供免费SSL证书，确保HTTPS连接
- 一个Repl项目只能绑定一个自定义域名
- DNS生效通常需要几分钟到几小时，请耐心等待
