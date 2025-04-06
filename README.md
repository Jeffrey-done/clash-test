# Clash配置合并工具 (GitHub Pages版)

这是使用GitHub Pages + GitHub Actions部署的Clash配置合并工具，可以定期自动获取、合并和优化Clash节点。

## 特点

- **全自动化** - 使用GitHub Actions定期更新配置
- **无需服务器** - 所有内容都托管在GitHub上，无需维护服务器
- **永不休眠** - 不像Replit等平台，不会因为不活跃而休眠
- **完全免费** - 使用GitHub免费服务，无需任何费用

## 使用方法

1. 访问 [GitHub Pages网站](https://你的用户名.github.io/clash-config-merger/) 查看最新配置
2. 点击"下载"按钮获取最新的Clash配置文件
3. 将下载的配置文件导入到Clash客户端
4. 配置文件每6小时自动更新一次

## 自己部署

如果你想自己部署一份，请按照以下步骤操作：

1. **Fork本仓库**

2. **启用GitHub Pages**
   - 进入仓库设置 -> Pages
   - Source选择"main分支"，文件夹选择"docs"
   - 保存设置

3. **配置URL源**
   - 编辑`config_urls.txt`文件，添加你的Clash配置URL
   - 每行一个URL，以#开头的行会被忽略

4. **手动触发工作流**
   - 进入Actions标签页
   - 选择"Merge Clash Configs"工作流
   - 点击"Run workflow"按钮

5. **等待构建完成**
   - 几分钟后，访问`https://你的用户名.github.io/clash-config-merger/`查看结果

## 自定义配置

1. **修改更新频率**:
   - 编辑`.github/workflows/merge-configs.yml`文件
   - 修改`cron`表达式，默认为`0 */6 * * *`（每6小时一次）

2. **添加代理**:
   - 在仓库设置 -> Secrets and variables -> Actions
   - 添加以下环境变量:
     - `USE_PROXY`: 设置为`true`
     - `PROXY_ADDRESS`: 代理地址，如`http://127.0.0.1:7890`

## 常见问题

**Q: 为什么选择GitHub Pages + Actions?**
A: 因为它们是免费的，永不休眠，且高度自动化。

**Q: 是否支持订阅链接?**
A: 目前只支持直接下载配置文件，不支持订阅链接。

**Q: 如何增加更多配置源?**
A: 编辑`config_urls.txt`文件，添加更多的配置URL。

**Q: 配置更新的频率是多少?**
A: 默认每6小时更新一次，可以在工作流文件中修改。

## 技术细节

- 前端: 纯静态HTML/JS/CSS，托管在GitHub Pages
- 后端: GitHub Actions定期运行Python脚本
- 数据存储: 所有配置都存储在GitHub仓库中
- 自动化: 使用GitHub Actions定时触发构建

# Clash配置合并工具 (Hugging Face Spaces版)

这是使用Hugging Face Spaces部署的Clash配置合并工具，可以定期自动获取、合并和优化Clash节点。

## 特点

- **多源合并** - 从多个URL获取并合并配置
- **节点优化** - 去重并测试节点延迟，按速度排序
- **用户友好** - 直观的Web界面，一键操作
- **完全免费** - 使用Hugging Face Spaces免费服务
- **永不休眠** - 不会因不活跃而休眠

## 使用方法

1. 访问 [Hugging Face Spaces应用](https://huggingface.co/spaces/你的用户名/clash-config-merger) 
2. 点击"运行合并任务"按钮开始处理
3. 等待任务完成，进度条显示当前进度
4. 在"配置文件"标签页下载生成的配置
5. 将配置文件导入到Clash客户端

## 自己部署

如果你想自己部署一份，请按照以下步骤操作：

1. **Fork本仓库**

2. **在Hugging Face创建新Space**
   - 访问 [Hugging Face Spaces](https://huggingface.co/spaces)
   - 点击 "Create a Space"
   - 选择 "Streamlit" 作为SDK
   - 选择 "From GitHub Repository" 作为源
   - 输入你的GitHub仓库URL
   - 点击 "Create Space"

3. **配置URL源**
   - 编辑`config_urls.txt`文件，添加你的Clash配置URL
   - 每行一个URL，以#开头的行会被忽略

4. **自定义配置**
   - 编辑`config.yaml`文件调整延迟测试参数
   - 修改输出文件名和目录

## Hugging Face vs Replit vs GitHub Pages

| 特性 | Hugging Face | Replit | GitHub Pages |
|------|-------------|--------|-------------|
| 运行后端代码 | ✅ | ✅ | ❌ |
| 延迟测试 | ✅ | ✅ | ❌ |
| 免费使用 | ✅ | ✅ (有限制) | ✅ |
| 不休眠 | ✅ | ❌ | ✅ |
| 自动部署 | ✅ | ✅ | ✅ |
| 资源限制 | 中等 | 较低 | 无后端 |

## 常见问题

**Q: 为什么选择Hugging Face Spaces?**
A: 因为它完全免费，不会休眠，且支持运行Python后端代码进行延迟测试。

**Q: 是否支持订阅链接?**
A: 目前只支持直接下载配置文件，不支持订阅链接。

**Q: 如何增加更多配置源?**
A: 编辑`config_urls.txt`文件，添加更多的配置URL。

**Q: 延迟测试占用资源大吗?**
A: 默认配置已经针对Hugging Face环境优化，设置了合理的并发数和超时时间。

## 技术细节

- 前端: Streamlit，提供简洁直观的Web界面
- 后端: Python，处理配置合并和节点测试
- 数据存储: 所有配置都存储在Hugging Face Spaces的持久存储中
- 资源利用: 优化的延迟测试参数，适合免费环境运行
