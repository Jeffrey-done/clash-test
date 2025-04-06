#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash配置文件合并与优化工具
"""

import os
import sys
import yaml
import logging
import asyncio
import time
from rich.console import Console
from rich.progress import Progress
from datetime import datetime

from utils.github_fetcher import GitHubFetcher
from utils.proxy_merger import ProxyMerger
from utils.latency_tester import LatencyTester
from utils.config_generator import ConfigGenerator

console = Console()

def setup_logging(config):
    """设置日志系统"""
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', 'clash_merger.log')
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[bold red]错误: 无法加载配置文件 - {str(e)}[/bold red]")
        sys.exit(1)

def ensure_output_dir(output_dir):
    """确保输出目录存在"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"已创建输出目录: {output_dir}")

async def main():
    """主函数"""
    console.print("[bold blue]Clash配置合并与优化工具[/bold blue]")
    console.print("正在启动...\n")
    
    # 加载配置
    config = load_config()
    logger = setup_logging(config)
    logger.info("程序启动")
    
    # 确保输出目录存在
    output_dir = config.get('output', {}).get('directory', 'output')
    ensure_output_dir(output_dir)
    
    # 实例化组件
    github_fetcher = GitHubFetcher(config)
    proxy_merger = ProxyMerger()
    latency_tester = LatencyTester(config)
    config_generator = ConfigGenerator(config)
    
    try:
        with Progress() as progress:
            # 计算待获取的配置文件总数
            repositories = config.get('repositories', []) or []
            yaml_urls = config.get('yaml_urls', []) or []
            local_files = config.get('local_files', []) or []
            total_sources = len(repositories) + len(yaml_urls) + len(local_files)
            
            if total_sources == 0:
                logger.warning("未配置任何配置源，请在config.yaml中添加yaml_urls、local_files或repositories")
                console.print("[bold yellow]警告: 未配置任何配置源，请在config.yaml中添加yaml_urls、local_files或repositories[/bold yellow]")
                return 1
            
            # 1. 获取配置文件
            task1 = progress.add_task("[cyan]正在获取配置文件...", total=total_sources)
            console.print("[bold cyan]正在获取配置文件...[/bold cyan]")
            
            raw_configs = await github_fetcher.fetch_all_configs(progress, task1)
            console.print(f"[green]成功获取 {len(raw_configs)} 个配置文件[/green]")
            
            if not raw_configs:
                logger.warning("未获取到任何有效的配置文件")
                console.print("[bold yellow]警告: 未获取到任何有效的配置文件，请检查网络连接或配置[/bold yellow]")
                return 1
            
            # 2. 合并代理节点
            console.print("[bold cyan]正在合并代理节点...[/bold cyan]")
            merged_proxies, first_config = proxy_merger.merge_proxies(raw_configs)
            console.print(f"[green]成功合并 {len(merged_proxies)} 个代理节点[/green]")
            
            if not merged_proxies:
                logger.warning("没有找到任何代理节点")
                console.print("[bold yellow]警告: 没有找到任何代理节点，请检查配置文件内容[/bold yellow]")
                return 1
            
            # 3. 去重代理节点
            console.print("[bold cyan]正在去除重复节点...[/bold cyan]")
            unique_proxies = proxy_merger.remove_duplicates(merged_proxies)
            console.print(f"[green]去重后剩余 {len(unique_proxies)} 个代理节点[/green]")
            
            # 4. 测试节点延迟
            console.print("[bold cyan]正在测试节点延迟...[/bold cyan]")
            tested_proxies = await latency_tester.test_all_proxies(unique_proxies)
            console.print(f"[green]延迟测试完成，有效节点数: {len(tested_proxies)}[/green]")
            
            # 5. 生成最终配置文件
            console.print("[bold cyan]正在生成最终配置文件...[/bold cyan]")
            output_file = os.path.join(output_dir, config.get('output', {}).get('filename', 'optimized_clash_config.yaml'))
            config_generator.generate_config(tested_proxies, first_config, output_file)
            
        console.print(f"\n[bold green]处理完成! 最终配置文件已保存到: {output_file}[/bold green]")
        console.print(f"共处理 {len(merged_proxies)} 个节点，去重后 {len(unique_proxies)} 个，最终有效节点 {len(tested_proxies)} 个")
        
    except Exception as e:
        logger.exception("处理过程中发生错误")
        console.print(f"[bold red]错误: {str(e)}[/bold red]")
        return 1
    
    return 0

if __name__ == "__main__":
    start_time = time.time()
    exit_code = asyncio.run(main())
    elapsed = time.time() - start_time
    print(f"\n总耗时: {elapsed:.2f} 秒")
    sys.exit(exit_code) 