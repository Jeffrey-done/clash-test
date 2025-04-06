#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash配置合并工具 - Web界面
"""

import os
import yaml
import json
import time
import logging
import asyncio
import subprocess
from datetime import datetime
import re
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from threading import Thread, Event
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入主程序组件
from utils.github_fetcher import GitHubFetcher
from utils.proxy_merger import ProxyMerger
from utils.latency_tester import LatencyTester
from utils.config_generator import ConfigGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("webui")

# 初始化Flask应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)  # 启用跨域请求支持

# 全局变量
CONFIG_FILE = os.environ.get('CONFIG_FILE', 'config.yaml')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
TASK_STATUS = {
    'running': False,
    'last_run': None,
    'progress': 0,
    'message': '准备就绪',
    'logs': []
}

def load_config():
    """加载配置文件"""
    try:
        # 首先尝试使用环境变量定义的配置文件
        if os.environ.get('USE_CLOUD_CONFIG', 'false').lower() == 'true':
            config_path = 'config_cloud.yaml'
        else:
            config_path = CONFIG_FILE
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 替换环境变量
        config_str = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        env_pattern = r'\${([A-Za-z0-9_]+)}'
        
        def replace_env_var(match):
            env_var = match.group(1)
            return os.environ.get(env_var, '')
            
        config_str = re.sub(env_pattern, replace_env_var, config_str)
        return yaml.safe_load(config_str)
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return {}

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {str(e)}")
        return False

def add_log(message, level="INFO"):
    """添加日志到状态中"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    TASK_STATUS['logs'].append(log_entry)
    TASK_STATUS['message'] = message
    # 限制日志数量，保留最新的100条
    if len(TASK_STATUS['logs']) > 100:
        TASK_STATUS['logs'] = TASK_STATUS['logs'][-100:]

def get_output_files():
    """获取输出目录中的文件列表"""
    files = []
    if os.path.exists(OUTPUT_DIR):
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                file_path = os.path.join(OUTPUT_DIR, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                size = os.path.getsize(file_path) / 1024  # KB
                files.append({
                    'name': filename,
                    'time': file_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{size:.1f} KB"
                })
    return sorted(files, key=lambda x: x['time'], reverse=True)

async def run_merger_task():
    """运行合并任务"""
    global TASK_STATUS
    
    # 更新任务状态
    TASK_STATUS['running'] = True
    TASK_STATUS['progress'] = 0
    TASK_STATUS['message'] = '开始处理...'
    add_log('任务开始', "INFO")
    
    # 保存中间结果用的变量
    tested_proxies = []
    first_config = None
    config = None
    output_dir = OUTPUT_DIR
    
    try:
        config = load_config()
        
        # 确保输出目录存在
        output_dir = config.get('output', {}).get('directory', OUTPUT_DIR)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 初始化组件
        github_fetcher = GitHubFetcher(config)
        proxy_merger = ProxyMerger()
        latency_tester = LatencyTester(config)
        config_generator = ConfigGenerator(config)
        
        # 1. 获取配置文件
        TASK_STATUS['progress'] = 10
        TASK_STATUS['message'] = '正在获取配置文件...'
        add_log('正在获取配置文件...', "INFO")
        
        raw_configs = await github_fetcher.fetch_all_configs(None, None)
        
        if not raw_configs:
            TASK_STATUS['message'] = '未获取到有效的配置文件'
            add_log('未获取到有效的配置文件，请检查网络和配置', "ERROR")
            TASK_STATUS['running'] = False
            return False
        
        add_log(f'成功获取 {len(raw_configs)} 个配置文件', "INFO")
        
        # 2. 合并代理节点
        TASK_STATUS['progress'] = 30
        TASK_STATUS['message'] = '正在合并代理节点...'
        add_log('正在合并代理节点...', "INFO")
        
        merged_proxies, first_config = proxy_merger.merge_proxies(raw_configs)
        
        if not merged_proxies:
            TASK_STATUS['message'] = '没有找到任何代理节点'
            add_log('没有找到任何代理节点，请检查配置文件内容', "ERROR")
            TASK_STATUS['running'] = False
            return False
        
        add_log(f'成功合并 {len(merged_proxies)} 个代理节点', "INFO")
        
        # 3. 去重代理节点
        TASK_STATUS['progress'] = 50
        TASK_STATUS['message'] = '正在去除重复节点...'
        add_log('正在去除重复节点...', "INFO")
        
        unique_proxies = proxy_merger.remove_duplicates(merged_proxies)
        add_log(f'去重后剩余 {len(unique_proxies)} 个代理节点', "INFO")
        
        # 4. 测试节点延迟
        TASK_STATUS['progress'] = 60
        TASK_STATUS['message'] = '正在测试节点延迟...'
        add_log('正在测试节点延迟...', "INFO")
        
        # 检查任务是否被取消
        if not TASK_STATUS['running']:
            add_log('任务已被取消，保存已处理的节点', "WARNING")
            return False
            
        # 修改为由latency_tester返回已测试节点的中间结果
        tested_proxies = await latency_tester.test_all_proxies(unique_proxies, TASK_STATUS)
        
        # 检查任务是否被取消
        if not TASK_STATUS['running']:
            # 如果任务被取消但已有部分测试结果，则保存这些结果
            if tested_proxies:
                add_log(f'任务已停止，但已有 {len(tested_proxies)} 个有效节点，将保存这些节点', "WARNING")
                # 保存中间结果
                output_file = os.path.join(output_dir, config.get('output', {}).get('filename', 'optimized_clash_config.yaml'))
                config_generator.generate_config(tested_proxies, first_config, output_file)
                add_log(f'已保存 {len(tested_proxies)} 个节点到 {output_file}', "INFO")
                TASK_STATUS['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return False
            
        add_log(f'延迟测试完成，有效节点数: {len(tested_proxies)}', "INFO")
        
        # 5. 生成最终配置文件
        TASK_STATUS['progress'] = 90
        TASK_STATUS['message'] = '正在生成最终配置文件...'
        add_log('正在生成最终配置文件...', "INFO")
        
        output_file = os.path.join(output_dir, config.get('output', {}).get('filename', 'optimized_clash_config.yaml'))
        config_generator.generate_config(tested_proxies, first_config, output_file)
        
        # 完成
        TASK_STATUS['progress'] = 100
        TASK_STATUS['message'] = '处理完成'
        add_log(f'任务完成！最终配置文件已保存到: {output_file}', "INFO")
        add_log(f'统计: 原始节点数 {len(merged_proxies)}，去重后 {len(unique_proxies)}，有效节点 {len(tested_proxies)}', "INFO")
        
        TASK_STATUS['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True
        
    except Exception as e:
        logger.exception("处理过程中发生错误")
        TASK_STATUS['message'] = f'处理失败: {str(e)}'
        add_log(f'处理失败: {str(e)}', "ERROR")
        
        # 如果有中间结果，仍然保存
        if tested_proxies and first_config and config:
            try:
                add_log(f'尝试保存中间结果: {len(tested_proxies)} 个有效节点', "INFO")
                output_file = os.path.join(output_dir, config.get('output', {}).get('filename', 'optimized_clash_config.yaml'))
                config_generator = ConfigGenerator(config)
                config_generator.generate_config(tested_proxies, first_config, output_file)
                add_log(f'已保存中间结果到 {output_file}', "INFO")
                TASK_STATUS['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            except Exception as save_err:
                add_log(f'保存中间结果失败: {str(save_err)}', "ERROR")
                
        return False
    finally:
        TASK_STATUS['running'] = False

@app.route('/')
def index():
    """主页"""
    config = load_config() or {}  # 确保config不为None
    output_files = get_output_files()
    return render_template('index.html', 
                           config=config, 
                           status=TASK_STATUS,
                           output_files=output_files)

@app.route('/config')
def config_page():
    """配置页面"""
    config = load_config() or {}  # 确保config不为None
    return render_template('config.html', config=config)

@app.route('/logs')
def logs_page():
    """日志页面"""
    return render_template('logs.html', logs=TASK_STATUS['logs'])

@app.route('/nodes')
def nodes_page():
    """节点页面"""
    # 获取最新生成的配置文件
    output_files = get_output_files()
    
    if not output_files:
        return render_template('nodes.html', nodes=[], error="未找到配置文件")
    
    latest_file = os.path.join(OUTPUT_DIR, output_files[0]['name'])
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        nodes = config_data.get('proxies', [])
        return render_template('nodes.html', nodes=nodes)
    except Exception as e:
        return render_template('nodes.html', nodes=[], error=f"读取配置文件失败: {str(e)}")

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """配置API"""
    if request.method == 'GET':
        return jsonify(load_config())
    
    if request.method == 'POST':
        try:
            new_config = request.json
            if save_config(new_config):
                return jsonify({"status": "success", "message": "配置已保存"})
            else:
                return jsonify({"status": "error", "message": "保存配置失败"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/status')
def api_status():
    """状态API"""
    return jsonify(TASK_STATUS)

@app.route('/api/run', methods=['POST'])
def api_run():
    """运行任务API"""
    if TASK_STATUS['running']:
        return jsonify({"status": "error", "message": "任务已在运行中"}), 400
    
    # 设置任务为运行状态
    TASK_STATUS['running'] = True
    TASK_STATUS['progress'] = 0
    TASK_STATUS['message'] = '已启动任务，正在初始化...'
    add_log('已启动任务，正在初始化...', "INFO")
    
    # 启动异步任务
    Thread(target=lambda: asyncio.run(run_merger_task())).start()
    
    # 立即返回，不等待任务完成
    return jsonify({
        "status": "success", 
        "message": "任务已启动，请通过状态API查询进度"
    })

@app.route('/api/logs')
def api_logs():
    """日志API"""
    return jsonify(TASK_STATUS['logs'])

@app.route('/api/files')
def api_files():
    """文件列表API"""
    return jsonify(get_output_files())

@app.route('/download/<filename>')
def download_file(filename):
    """下载文件"""
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/view/<filename>')
def view_file(filename):
    """查看文件内容"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('view_file.html', filename=filename, content=content)
    except Exception as e:
        return f"读取文件失败: {str(e)}", 500

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """清除日志API"""
    TASK_STATUS['logs'] = []
    return jsonify({"status": "success", "message": "日志已清除"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """停止任务API"""
    if not TASK_STATUS['running']:
        return jsonify({"status": "error", "message": "任务未在运行中"}), 400
    
    # 设置任务为停止状态
    TASK_STATUS['running'] = False
    TASK_STATUS['progress'] = 0
    TASK_STATUS['message'] = '任务已停止，已保存已测试的节点'
    add_log('任务已停止，已保存已测试的节点', "INFO")
    
    return jsonify({
        "status": "success", 
        "message": "任务已停止，已保存已测试的节点"
    })

if __name__ == '__main__':
    # 确保输出目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 获取端口号和主机从环境变量
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # 启动Flask应用
    app.run(host=host, port=port, debug=debug) 