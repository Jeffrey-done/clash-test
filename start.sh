#!/bin/bash
echo "开始准备环境..."

# 创建必要目录
mkdir -p output

# 安装依赖
python -m pip install -r requirements.txt

# 启动应用
echo "启动应用..."
python webui.py 