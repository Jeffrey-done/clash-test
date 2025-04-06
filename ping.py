#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自我ping脚本 - 保持Replit应用处于活跃状态
支持默认Replit域名和自定义域名
"""

import time
import requests
import logging
import os
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ping.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("ping")

# 应用URL配置
# 1. 首先尝试从环境变量获取应用URL
# 2. 如果未设置，则使用默认的Replit域名格式
DEFAULT_REPLIT_URL = "https://clash-config-merger.用户名.repl.co"
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "")
APP_URL = os.environ.get("APP_URL", CUSTOM_DOMAIN if CUSTOM_DOMAIN else DEFAULT_REPLIT_URL)

# ping间隔(秒)，默认15分钟，可通过环境变量自定义
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", 900))

# 超时设置（秒）
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 10))

# 统计信息
ping_stats = {
    "total": 0,
    "success": 0,
    "failure": 0,
    "total_time": 0,
    "min_time": float('inf'),
    "max_time": 0,
    "start_time": datetime.now()
}

def ping_app():
    """
    ping应用并返回状态码和响应时间
    
    Returns:
        tuple: (状态码, 响应时间) 如果请求失败则返回 (None, None)
    """
    try:
        start_time = time.time()
        response = requests.get(APP_URL, timeout=REQUEST_TIMEOUT)
        elapsed = time.time() - start_time
        
        # 更新统计信息
        ping_stats["total"] += 1
        ping_stats["success"] += 1
        ping_stats["total_time"] += elapsed
        ping_stats["min_time"] = min(ping_stats["min_time"], elapsed)
        ping_stats["max_time"] = max(ping_stats["max_time"], elapsed)
        
        return response.status_code, elapsed
    except Exception as e:
        ping_stats["total"] += 1
        ping_stats["failure"] += 1
        logger.error(f"请求失败: {str(e)}")
        return None, None

def format_timespan(seconds):
    """
    将秒数格式化为人类可读的时间跨度
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化后的时间跨度 (例如: "2天 3小时 45分钟 30秒")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days: parts.append(f"{int(days)}天")
    if hours: parts.append(f"{int(hours)}小时")
    if minutes: parts.append(f"{int(minutes)}分钟")
    if seconds or not parts: parts.append(f"{int(seconds)}秒")
    
    return " ".join(parts)

def print_stats():
    """打印当前的ping统计信息"""
    run_time = datetime.now() - ping_stats["start_time"]
    run_time_seconds = run_time.total_seconds()
    
    avg_time = ping_stats["total_time"] / ping_stats["success"] if ping_stats["success"] > 0 else 0
    
    logger.info(f"===== Ping统计信息 =====")
    logger.info(f"服务运行时间: {format_timespan(run_time_seconds)}")
    logger.info(f"总ping次数: {ping_stats['total']}")
    logger.info(f"成功次数: {ping_stats['success']} ({ping_stats['success']/ping_stats['total']*100:.1f}% 成功率)")
    logger.info(f"失败次数: {ping_stats['failure']}")
    
    if ping_stats["success"] > 0:
        logger.info(f"平均响应时间: {avg_time:.2f}秒")
        logger.info(f"最快响应时间: {ping_stats['min_time']:.2f}秒")
        logger.info(f"最慢响应时间: {ping_stats['max_time']:.2f}秒")
    
    logger.info(f"目标URL: {APP_URL}")
    logger.info(f"========================")

def main():
    """主函数 - 启动ping服务并定期ping应用"""
    logger.info(f"启动自我ping服务...")
    logger.info(f"目标URL: {APP_URL}")
    logger.info(f"ping间隔: {PING_INTERVAL}秒")
    logger.info(f"请求超时: {REQUEST_TIMEOUT}秒")
    
    if APP_URL == DEFAULT_REPLIT_URL:
        logger.warning(f"你正在使用默认URL，请确保将其修改为你的实际Replit URL或自定义域名")
    
    # 下次统计信息打印时间
    next_stats_time = datetime.now() + timedelta(hours=1)
    
    try:
        while True:
            status, elapsed = ping_app()
            
            if status:
                logger.info(f"Ping成功: 状态码={status}, 耗时={elapsed:.2f}秒")
            else:
                logger.warning(f"Ping失败")
            
            # 每小时打印一次统计信息
            if datetime.now() >= next_stats_time:
                print_stats()
                next_stats_time = datetime.now() + timedelta(hours=1)
            
            # 等待下一次ping
            logger.info(f"等待{PING_INTERVAL}秒后进行下一次ping...")
            time.sleep(PING_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("收到终止信号，ping服务停止")
    except Exception as e:
        logger.error(f"ping服务发生错误: {str(e)}")
        raise
    finally:
        logger.info("ping服务已终止")
        print_stats()  # 打印最终统计信息

if __name__ == "__main__":
    main() 