#!/usr/bin/env python3
import sys
import subprocess
import os

def run_command(command):
    print(f"执行: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误 (代码 {result.returncode}):")
        print(result.stderr)
        return False
    print("成功!")
    return True

def install_packages():
    packages = [
        "Flask==2.2.3",
        "Flask-Cors==3.0.10",
        "requests==2.28.2",
        "python-dotenv==1.0.0",
        "rich==13.3.2",
        "gunicorn==20.1.0"
    ]
    
    # 尝试用不同的方法安装PyYAML
    yaml_installed = False
    
    # 方法1: 使用预编译wheel
    if run_command("pip install --only-binary :all: PyYAML==6.0"):
        yaml_installed = True
    
    # 方法2: 禁用构建隔离
    if not yaml_installed and run_command("pip install pyyaml==6.0 --no-build-isolation"):
        yaml_installed = True
    
    # 方法3: 使用系统包管理器
    if not yaml_installed:
        if sys.platform == "linux":
            run_command("apt-get update && apt-get install -y python3-yaml")
        yaml_installed = True
    
    # 安装其他包
    for package in packages:
        run_command(f"pip install {package}")
    
    print("\n依赖安装结果:")
    run_command("pip list")

if __name__ == "__main__":
    print("开始安装Python依赖...")
    install_packages()
    print("安装过程完成!") 