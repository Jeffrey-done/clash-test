#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gunicorn配置文件 - 用于生产环境部署
"""

import multiprocessing

# 绑定的地址和端口
bind = "0.0.0.0:8080"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"

# 超时时间
timeout = 120

# 日志配置
loglevel = "info"
accesslog = "access.log"
errorlog = "error.log"

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 预加载应用
preload_app = True

# 工作模式
daemon = False

# 配置应用
wsgi_app = "webui:app" 