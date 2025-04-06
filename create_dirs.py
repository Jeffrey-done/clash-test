#!/usr/bin/env python3
import os

# 创建必要的目录
dirs = ['output']
for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)
        print(f"创建目录: {d}")
    else:
        print(f"目录已存在: {d}")

print("目录检查完成，应用准备就绪") 