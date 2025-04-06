# 在Hugging Face Spaces上部署Clash配置合并工具

本文档详细说明了如何将Clash配置合并工具从Flask版本修改为适合在Hugging Face Spaces上运行的Streamlit版本。

## 已完成的修改

1. **添加Streamlit支持**:
   - 创建了`app.py`作为Streamlit应用的入口点
   - 更新了`requirements.txt`添加Streamlit依赖

2. **优化延迟测试**:
   - 修改`latency_tester.py`，降低默认并发数从50到20
   - 减少超时时间从5000ms到2000ms
   - 增加了批次间隔参数，默认1秒
   - 添加了最大节点数限制，默认300个

3. **改进脚本**:
   - 重写了`run_task.py`，使其独立于Flask应用运行
   - 添加了日期格式化的配置文件命名
   - 同时生成每日配置和latest.yaml文件

4. **部署配置**:
   - 创建了`app.sh`启动脚本，自动设置环境
   - 添加了`.gitattributes`用于大文件处理
   - 创建`Procfile`定义启动命令

5. **文档更新**:
   - 重写了`README.md`，添加Hugging Face Spaces部署说明
   - 创建了`README-hf.md`用于Hugging Face界面显示

## 如何使用

1. **本地测试**:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

2. **部署到Hugging Face Spaces**:
   - 在Hugging Face创建新Space，选择Streamlit SDK
   - 连接到GitHub仓库或上传文件
   - 确保Space中有`app.py`和`requirements.txt`

3. **自定义部署**:
   - 修改`config_urls.txt`添加你自己的配置源
   - 调整`config.yaml`中的参数
   - 更新`README-hf.md`添加你的用户名

## 环境变量配置

Hugging Face Spaces允许设置环境变量，可以在Space设置中添加:

- `OUTPUT_DIR`: 输出目录路径 (默认: "output")
- `CONFIG_FILE`: 配置文件路径 (默认: "config.yaml")
- `URL_SOURCE_FILE`: URL源文件路径 (默认: "config_urls.txt")

## 注意事项

1. **资源限制**:
   - Hugging Face免费空间有CPU和内存限制
   - 通过降低并发数和超时时间，我们优化了资源使用

2. **持久存储**:
   - Hugging Face Spaces提供持久存储，配置文件不会丢失
   - 每次更新代码会重置环境，但不会删除生成的文件

3. **休眠策略**:
   - 不同于Replit，Hugging Face Spaces不会因为不活跃而休眠
   - 不需要ping服务来保持活跃

## 对比其他平台

我们的Streamlit版本可以在多个平台运行，各有优缺点:

| 平台 | 延迟测试 | 免费程度 | 资源限制 | 休眠策略 | 易用性 |
|------|---------|---------|---------|---------|--------|
| Hugging Face | ✅ | 完全免费 | 中等 | 不休眠 | 简单 |
| Replit | ✅ | 有限制 | 低 | 会休眠 | 简单 |
| GitHub Pages | ❌ | 完全免费 | 无后端 | 不休眠 | 中等 |
| Railway | ✅ | 免费有时限 | 高 | 不休眠 | 中等 |

## 文件列表

```
.
├── app.py                # Streamlit应用入口
├── app.sh                # 启动脚本
├── config.yaml           # 配置文件
├── config.yaml.example   # 配置文件示例
├── config_urls.txt       # URL源文件
├── config_urls.txt.example # URL源文件示例
├── .gitattributes        # Git大文件配置
├── Procfile              # 部署配置
├── README.md             # 主说明文档
├── README-hf.md          # Hugging Face界面说明
├── requirements.txt      # 依赖列表
├── run_task.py           # 后台任务运行脚本
└── utils/                # 工具模块
    ├── __init__.py
    ├── config_generator.py
    ├── github_fetcher.py
    ├── latency_tester.py
    └── proxy_merger.py
``` 