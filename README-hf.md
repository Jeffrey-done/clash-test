# Clash配置合并工具

[![Open In Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/你的用户名/clash-config-merger)

## 简介

这是一个自动获取、合并和优化Clash代理配置的工具。它可以从多个来源获取配置，合并所有节点，测试它们的延迟，并生成优化后的配置文件。

## 功能特点

- **多源合并**: 支持从多个URL源获取配置
- **节点去重**: 自动删除重复的节点
- **延迟测试**: 测试每个节点的连接延迟
- **排序优化**: 按延迟从低到高排序节点
- **用户友好**: 简洁直观的Web界面
- **完全免费**: 基于Hugging Face Spaces部署，无需服务器
- **永不休眠**: 不会因为不活跃而自动休眠

## 使用方法

1. 点击"运行合并任务"按钮开始处理
2. 等待任务完成，进度条显示当前进度
3. 在"配置文件"标签页下载生成的配置
4. 将配置文件导入到Clash客户端

## 进阶技巧

- 可以在[GitHub仓库](https://github.com/你的用户名/clash-test)查看源代码
- 编辑`config_urls.txt`可以添加更多配置源
- 调整`config.yaml`中的测试参数优化延迟测试

## 关于部署

本应用部署在Hugging Face Spaces上，完全免费且不会休眠，具有以下优势：

- 完整支持延迟测试功能
- 无需信用卡或付费
- 不存在休眠问题
- 部署简单方便

## 隐私说明

本应用不会收集任何个人信息，所有操作都在服务器端完成。生成的配置文件只保存在应用的存储空间中，可随时下载或删除。 