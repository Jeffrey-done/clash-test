#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
后台任务运行器 - 运行Clash配置合并任务
Hugging Face Spaces优化版
"""

import os
import sys
import yaml
import asyncio
import time
import logging
from datetime import datetime
from rich.console import Console

# 导入主程序组件
from utils.github_fetcher import GitHubFetcher
from utils.proxy_merger import ProxyMerger
from utils.latency_tester import LatencyTester
from utils.config_generator import ConfigGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clash_merger.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_task")

console = Console()

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
    console.print("[bold blue]Clash配置合并与优化工具 (Hugging Face版)[/bold blue]")
    console.print("正在启动...\n")
    
    # 加载配置
    config = load_config()
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
        # 1. 获取配置文件
        console.print("[bold cyan]正在获取配置文件...[/bold cyan]")
        raw_configs = await github_fetcher.fetch_all_configs(None, None)
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
        
        # 获取最大节点数限制
        max_nodes = config.get('latency_test', {}).get('max_nodes', 300)
        if len(unique_proxies) > max_nodes:
            logger.warning(f"节点数量({len(unique_proxies)})超过最大限制({max_nodes})，将随机选择{max_nodes}个节点进行测试")
            console.print(f"[bold yellow]警告: 节点数量过多，将只测试{max_nodes}个节点[/bold yellow]")
            import random
            random.shuffle(unique_proxies)
            unique_proxies = unique_proxies[:max_nodes]
        
        tested_proxies = await latency_tester.test_all_proxies(unique_proxies)
        console.print(f"[green]延迟测试完成，有效节点数: {len(tested_proxies)}[/green]")
        
        # 5. 生成最终配置文件
        console.print("[bold cyan]正在生成最终配置文件...[/bold cyan]")
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 生成每日配置文件
        daily_filename = f"clash_config_{timestamp}.yaml"
        daily_output_file = os.path.join(output_dir, daily_filename)
        config_generator.generate_config(tested_proxies, first_config, daily_output_file)
        
        # 同时生成latest.yaml
        latest_output_file = os.path.join(output_dir, "latest.yaml")
        config_generator.generate_config(tested_proxies, first_config, latest_output_file)
        
        console.print(f"\n[bold green]处理完成! 配置文件已保存:[/bold green]")
        console.print(f"1. 每日配置: {daily_output_file}")
        console.print(f"2. 最新配置: {latest_output_file}")
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