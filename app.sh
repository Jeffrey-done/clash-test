#!/bin/bash

# 检查当前目录
echo "当前目录: $(pwd)"

# 检查是否存在app.py
if [ ! -f "app.py" ]; then
    echo "错误: app.py文件不存在!"
    exit 1
fi

# 确保目录存在
mkdir -p output

# 检查系统
echo "系统信息:"
uname -a
python --version

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 确保配置文件存在
if [ ! -f "config.yaml" ]; then
    echo "创建默认配置文件..."
    cp config.yaml.example config.yaml || echo "无法创建配置文件!"
fi

# 确保URL源文件存在
if [ ! -f "config_urls.txt" ]; then
    echo "创建默认URL源文件..."
    cp config_urls.txt.example config_urls.txt || echo "无法创建URL源文件!"
fi

# 修改延迟测试参数以适配HF环境
echo "优化配置参数..."
if [ -f "config.yaml" ]; then
    sed -i 's/concurrent_tests: 100/concurrent_tests: 20/g' config.yaml
    sed -i 's/timeout: 3000/timeout: 2000/g' config.yaml
    sed -i 's/enable: true/enable: false/g' config.yaml
    echo "配置参数已优化"
else
    echo "警告: 配置文件不存在，无法优化参数"
fi

# 列出重要文件
echo "文件列表:"
ls -la

# 启动应用
echo "启动应用..."
echo "执行命令: streamlit run app.py --server.port=7860 --server.address=0.0.0.0"
streamlit run app.py --server.port=7860 --server.address=0.0.0.0 