# Clash 配置合并工具

这是一个用于合并多个Clash配置文件的工具，它可以获取多个配置源，合并节点，测试延迟，并生成优化后的配置文件。

## 特性

- 支持从多个URL和本地文件加载配置
- 自动合并和去重代理节点
- 节点延迟测试和排序
- Web界面进行配置和管理
- 支持中断任务并保存中间结果

## 云端部署

### Cloudflare Pages 部署

1. Fork本仓库到你的GitHub账户
2. 在Cloudflare Dashboard创建一个新的Pages项目
3. 连接你的GitHub仓库
4. 设置以下环境变量:
   - `USE_CLOUD_CONFIG`: true
   - `URL_SOURCE_FILE`: 配置链接的TXT文件路径（默认为config_urls.txt）
   - `PROXY_ENABLE`: true/false
   - `PROXY_ADDRESS`: 你的HTTP代理地址(如果启用)

### 使用GitHub Actions自动部署

1. 在GitHub仓库设置中添加以下Secrets:
   - `CLOUDFLARE_API_TOKEN`: 你的Cloudflare API Token
   - `CLOUDFLARE_ACCOUNT_ID`: 你的Cloudflare账户ID
2. 推送代码到main分支将自动触发部署

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

## 许可证

MIT
