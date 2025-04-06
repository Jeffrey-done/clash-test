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

## 保持Replit应用长期运行

1. 注册[UptimeRobot](https://uptimerobot.com/)账号
2. 添加新的监控器
   - 类型：HTTP(s)
   - 名称：任意(例如"Clash合并工具")
   - URL：你的Replit应用URL
   - 监控间隔：设置为5分钟

## 许可证

MIT
