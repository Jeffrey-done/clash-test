#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
后台任务运行器 - 运行Clash配置合并任务
"""

import asyncio
from webui import run_merger_task

if __name__ == "__main__":
    # 运行合并任务
    asyncio.run(run_merger_task()) 