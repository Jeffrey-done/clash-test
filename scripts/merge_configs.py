#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash配置合并脚本 - GitHub Actions版本
专为GitHub Pages + Actions设计的精简版，不需要UI和交互
"""

import os
import sys
import yaml
import json
import logging
import asyncio
import time
import requests
from datetime import datetime
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 常量定义
CONFIGS_DIR = 'docs/configs'
CONFIG_URLS_FILE = 'config_urls.txt'
DEFAULT_TIMEOUT = 30  # 请求超时时间 (秒)
MAX_CONCURRENT_REQUESTS = 10  # 最大并发请求数

# 确保输出目录存在
os.makedirs(CONFIGS_DIR, exist_ok=True)

# 使用的代理配置（默认不使用）
proxies = None

# 从环境变量读取配置
if os.environ.get('USE_PROXY', 'false').lower() == 'true':
    proxy_address = os.environ.get('PROXY_ADDRESS', '')
    if proxy_address:
        proxies = {
            'http': proxy_address,
            'https': proxy_address
        }
        logger.info(f"使用代理: {proxy_address}")

async def fetch_config(url):
    """异步获取配置文件"""
    try:
        # 使用requests而不是aiohttp，因为GitHub Actions环境更兼容
        # 对于少量请求，同步请求影响不大
        response = requests.get(url, timeout=DEFAULT_TIMEOUT, proxies=proxies)
        response.raise_for_status()
        
        # 尝试解析YAML
        try:
            config = yaml.safe_load(response.text)
            if not isinstance(config, dict) or 'proxies' not in config:
                logger.warning(f"无效的Clash配置: {url}")
                return None
            return config
        except Exception as e:
            logger.warning(f"解析配置失败: {url}, 错误: {str(e)}")
            return None
            
    except Exception as e:
        logger.warning(f"获取配置失败: {url}, 错误: {str(e)}")
        return None

def load_urls_from_file():
    """从文件加载URL列表"""
    urls = []
    try:
        if os.path.exists(CONFIG_URLS_FILE):
            with open(CONFIG_URLS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
            logger.info(f"从文件加载了 {len(urls)} 个URL")
    except Exception as e:
        logger.error(f"加载URL文件失败: {str(e)}")
    return urls

def merge_proxies(configs):
    """合并代理节点并去重"""
    if not configs:
        return [], None
        
    all_proxies = []
    first_config = None
    
    # 获取第一个有效配置作为模板
    for config in configs:
        if config and isinstance(config, dict):
            first_config = config.copy()
            break
    
    # 如果没有找到有效配置，使用默认模板
    if not first_config:
        first_config = {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': True,
            'mode': 'rule',
            'log-level': 'info',
            'proxies': [],
            'proxy-groups': [
                {
                    'name': '🚀 节点选择',
                    'type': 'select',
                    'proxies': ['DIRECT']
                }
            ],
            'rules': ['MATCH,DIRECT']
        }
    
    # 收集所有代理
    for config in configs:
        if not config or not isinstance(config, dict):
            continue
            
        proxies = config.get('proxies', [])
        if not proxies or not isinstance(proxies, list):
            continue
            
        all_proxies.extend(proxies)
    
    logger.info(f"收集到 {len(all_proxies)} 个代理节点")
    
    # 去重代理
    unique_proxies = remove_duplicate_proxies(all_proxies)
    logger.info(f"去重后剩余 {len(unique_proxies)} 个代理节点")
    
    return unique_proxies, first_config

def remove_duplicate_proxies(proxies):
    """去除重复的代理节点"""
    unique_dict = {}
    
    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue
            
        # 跳过无效代理
        if 'name' not in proxy or 'type' not in proxy or 'server' not in proxy or 'port' not in proxy:
            continue
            
        # 生成唯一标识
        proxy_copy = proxy.copy()
        proxy_copy.pop('name', None)  # 名称可能会被修改，但节点本身可能相同
        
        try:
            proxy_str = json.dumps(proxy_copy, sort_keys=True)
            proxy_hash = hashlib.md5(proxy_str.encode()).hexdigest()
            unique_dict[proxy_hash] = proxy
        except:
            continue
    
    return list(unique_dict.values())

def generate_config(proxies, template, filename):
    """生成Clash配置文件"""
    if not proxies:
        logger.warning("没有有效的代理节点，无法生成配置")
        return False
        
    # 复制模板配置
    new_config = template.copy()
    
    # 更新代理列表
    new_config['proxies'] = proxies
    
    # 更新代理组
    if 'proxy-groups' in new_config:
        proxy_names = [p.get('name') for p in proxies]
        
        for group in new_config['proxy-groups']:
            # 如果是选择类型的代理组，更新代理列表
            if group.get('type') in ['select', 'url-test', 'fallback', 'load-balance']:
                # 添加所有代理和必要的选项
                group['proxies'] = proxy_names + ['DIRECT']
    
    # 添加元数据
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'metadata' not in new_config:
        new_config['metadata'] = {}
        
    new_config['metadata'].update({
        'updated': timestamp,
        'proxy_count': len(proxies),
        'generated_by': 'GitHub Actions'
    })
    
    # 输出到文件
    output_path = os.path.join(CONFIGS_DIR, filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        
        # 保存节点数量到文件，供前端使用
        with open(os.path.join(CONFIGS_DIR, 'node_count.txt'), 'w') as f:
            f.write(str(len(proxies)))
            
        logger.info(f"配置已保存到: {output_path}")
        return True
    except Exception as e:
        logger.error(f"保存配置失败: {str(e)}")
        return False

async def main():
    """主函数"""
    start_time = time.time()
    logger.info("开始处理配置合并")
    
    # 加载URL
    urls = load_urls_from_file()
    if not urls:
        logger.error("没有找到有效的配置URL")
        return 1
    
    # 获取配置
    configs = []
    for url in urls:
        config = await fetch_config(url)
        if config:
            configs.append(config)
    
    if not configs:
        logger.error("没有获取到有效的配置")
        return 1
    
    # 合并和去重代理
    proxies, template = merge_proxies(configs)
    if not proxies:
        logger.error("没有有效的代理节点")
        return 1
    
    # 生成配置文件
    output_filename = f"clash_config_{datetime.now().strftime('%Y%m%d')}.yaml"
    if generate_config(proxies, template, output_filename):
        # 生成最新版本的副本
        generate_config(proxies, template, "latest.yaml")
    
    elapsed = time.time() - start_time
    logger.info(f"处理完成，用时 {elapsed:.2f} 秒")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 