#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自我ping脚本 - 保持Replit应用处于活跃状态
"""

import time
import requests
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ping")

# 应用URL - 替换为你的实际URL
# 如果设置了环境变量APP_URL，则使用环境变量
APP_URL = os.environ.get("APP_URL", "https://你的应用名.用户名.repl.co")
# ping间隔(秒)，默认15分钟
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", 900))

def ping_app():
    """ping应用并返回状态码"""
    try:
        start_time = time.time()
        response = requests.get(APP_URL, timeout=10)
        elapsed = time.time() - start_time
        return response.status_code, elapsed
    except Exception as e:
        logger.error(f"请求失败: {str(e)}")
        return None, None

def main():
    """主函数"""
    logger.info(f"启动自我ping服务...")
    logger.info(f"目标URL: {APP_URL}")
    logger.info(f"ping间隔: {PING_INTERVAL}秒")
    
    ping_count = 0
    start_time = datetime.now()
    
    try:
        while True:
            ping_count += 1
            logger.info(f"执行第{ping_count}次ping...")
            
            status, elapsed = ping_app()
            
            if status:
                logger.info(f"Ping成功: 状态码={status}, 耗时={elapsed:.2f}秒")
            else:
                logger.warning(f"Ping失败")
            
            # 显示运行时间
            run_time = datetime.now() - start_time
            days = run_time.days
            hours, remainder = divmod(run_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(f"服务已运行: {days}天 {hours}小时 {minutes}分钟 {seconds}秒")
            
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

if __name__ == "__main__":
    main() 