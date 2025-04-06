#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash配置合并工具 - Streamlit界面
适配Hugging Face Spaces部署
"""

import streamlit as st
import subprocess
import os
import yaml
import time
import json
from datetime import datetime
import glob
import asyncio
import threading

# 设置页面标题和图标
st.set_page_config(
    page_title="Clash配置合并工具",
    page_icon="⚡",
    layout="wide"
)

# 常量定义
OUTPUT_DIR = "output"
CONFIG_FILE = "config.yaml"
URL_SOURCE_FILE = "config_urls.txt"
LOG_FILE = "clash_merger.log"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 函数：加载配置
def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"加载配置文件失败: {str(e)}")
        return {}

# 函数：加载URL列表
def load_urls():
    try:
        if not os.path.exists(URL_SOURCE_FILE):
            return []
        
        with open(URL_SOURCE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        urls = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
        
        return urls
    except Exception as e:
        st.error(f"加载URL文件失败: {str(e)}")
        return []

# 函数：读取日志文件
def read_logs(max_lines=100):
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines[-max_lines:] if lines else []
    except Exception as e:
        st.error(f"读取日志失败: {str(e)}")
        return []

# 函数：获取配置文件列表
def get_output_files():
    if not os.path.exists(OUTPUT_DIR):
        return []
    
    files = []
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith('.yaml') or file.endswith('.yml'):
            file_path = os.path.join(OUTPUT_DIR, file)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            size = os.path.getsize(file_path) / 1024  # KB
            
            # 尝试读取节点数量
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    proxies_count = len(content.get('proxies', []))
            except:
                proxies_count = 0
            
            files.append({
                'name': file,
                'path': file_path,
                'modified': last_modified,
                'size': size,
                'node_count': proxies_count
            })
    
    # 按修改时间排序
    return sorted(files, key=lambda x: x['modified'], reverse=True)

# 函数：运行合并任务
def run_merger_task():
    process = subprocess.Popen(
        ["python", "run_task.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 模拟进度
    for i in range(101):
        # 检查进程是否仍在运行
        if process.poll() is not None:
            break
        
        status_text.text(f"正在处理... {i}%")
        progress_bar.progress(i)
        time.sleep(0.5)
    
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        status_text.text("处理完成！")
        progress_bar.progress(100)
        return True, stdout
    else:
        status_text.text("处理失败！")
        return False, stderr

# 页面标题
st.title("⚡ Clash配置合并工具")
st.write("自动获取、合并和优化Clash代理配置")

# 创建标签页
tab1, tab2, tab3, tab4 = st.tabs(["首页", "配置文件", "日志", "关于"])

# 侧边栏
with st.sidebar:
    st.header("操作")
    
    # 运行按钮
    if st.button("运行合并任务", type="primary", key="run_task"):
        with st.spinner("正在运行合并任务..."):
            success, output = run_merger_task()
            
            if success:
                st.success("任务成功完成!")
            else:
                st.error("任务运行失败!")
                st.code(output)
    
    # 显示当前配置
    st.header("当前配置")
    config = load_config()
    
    st.subheader("延迟测试")
    st.write(f"并发数: {config.get('latency_test', {}).get('concurrent_tests', 50)}")
    st.write(f"超时(毫秒): {config.get('latency_test', {}).get('timeout', 3000)}")
    
    # 显示URL源
    st.subheader("配置源")
    urls = load_urls()
    st.write(f"URL数量: {len(urls)}")
    
    with st.expander("查看所有URL"):
        for url in urls:
            st.code(url, language=None)

# 首页内容
with tab1:
    st.header("系统状态")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("最近更新")
        files = get_output_files()
        if files:
            latest_file = files[0]
            st.info(f"最新文件: {latest_file['name']}")
            st.info(f"更新时间: {latest_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.info(f"节点数量: {latest_file['node_count']}")
        else:
            st.warning("尚未生成配置文件")
    
    with col2:
        st.subheader("环境信息")
        st.info(f"运行平台: Hugging Face Spaces")
        st.info(f"配置源数: {len(load_urls())}")
        
        # 显示日志文件大小
        if os.path.exists(LOG_FILE):
            log_size = os.path.getsize(LOG_FILE) / 1024  # KB
            st.info(f"日志大小: {log_size:.1f} KB")

# 配置文件标签页
with tab2:
    st.header("生成的配置文件")
    
    files = get_output_files()
    if not files:
        st.warning("暂无配置文件，请点击侧边栏的'运行合并任务'按钮生成")
    else:
        for file in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{file['name']}**")
                st.write(f"修改时间: {file['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.write(f"大小: {file['size']:.1f} KB")
                st.write(f"节点数: {file['node_count']}")
            
            with col3:
                with open(file['path'], 'rb') as f:
                    st.download_button(
                        label="下载",
                        data=f,
                        file_name=file['name'],
                        mime="application/x-yaml",
                        key=f"download_{file['name']}"
                    )
                
                if st.button("查看", key=f"view_{file['name']}"):
                    with open(file['path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    st.code(content, language="yaml")
            
            st.divider()

# 日志标签页
with tab3:
    st.header("运行日志")
    
    # 添加刷新按钮
    if st.button("刷新日志"):
        st.experimental_rerun()
    
    # 显示日志
    logs = read_logs(200)  # 最多显示200行
    if not logs:
        st.info("暂无日志记录")
    else:
        log_text = "".join(logs)
        st.text_area("日志内容", log_text, height=400)

# 关于标签页
with tab4:
    st.header("关于本工具")
    
    st.markdown("""
    ### Clash配置合并工具
    
    本工具可以自动从多个来源获取Clash配置，合并所有节点，进行去重和延迟测试，最后生成优化后的配置文件。
    
    #### 特点
    
    - **多源合并**: 支持从多个URL源获取配置
    - **节点去重**: 自动删除重复的节点
    - **延迟测试**: 测试每个节点的连接延迟
    - **排序优化**: 按延迟从低到高排序节点
    - **完全开源**: 代码开源，支持自定义
    
    #### 部署信息
    
    本应用部署在Hugging Face Spaces，完全免费且不会休眠。
    
    #### 源码地址
    
    [GitHub仓库](https://github.com/你的用户名/clash-test)
    """)

    st.info("本应用使用HuggingFace Spaces托管，完全免费且支持延迟测试功能") 