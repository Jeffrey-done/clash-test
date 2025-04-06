#!/bin/bash
echo "开始准备环境..."

# 创建必要目录
mkdir -p output

# 使用Python脚本安装依赖
echo "安装依赖..."
python install_deps.py

# 如果安装失败，尝试使用pip直接安装
if [ $? -ne 0 ]; then
  echo "尝试直接安装基本依赖..."
  pip install flask flask-cors
  pip install aiohttp asyncio
  pip install pyyaml requests
fi

# 尝试直接安装aiohttp和asyncio（以防安装脚本漏掉了这些）
pip install aiohttp
pip install asyncio

# 显示已安装的包
pip list

# 启动应用
echo "启动应用..."
python webui.py 