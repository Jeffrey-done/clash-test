# GitHub Pages 部署说明

此目录包含GitHub Pages静态网站文件。部署过程中，此目录会包含：

- 前端HTML/JS/CSS文件
- 生成的配置文件（在`configs/`子目录）

## 目录结构

```
docs/
├── index.html       # 主页
├── README.md        # 本说明文件
└── configs/         # 配置文件目录
    ├── latest.yaml  # 最新配置
    └── clash_config_YYYYMMDD.yaml  # 每日配置（日期格式）
```

## 自动化部署

配置文件通过GitHub Actions自动生成并提交到此目录。
详情请参考仓库根目录的`.github/workflows/merge-configs.yml`文件。 