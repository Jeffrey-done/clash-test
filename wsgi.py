#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WSGI配置文件 - 用于生产环境部署
"""

from webui import app

if __name__ == "__main__":
    app.run() 