#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置生成器 - 生成优化后的Clash配置文件
"""

import os
import yaml
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigGenerator:
    """配置生成器，用于生成优化后的Clash配置文件"""
    
    def __init__(self, config):
        """初始化配置生成器
        
        Args:
            config: 程序配置
        """
        self.config = config
        self.output_config = config.get('output', {})
    
    def _create_backup(self, output_file):
        """创建备份文件
        
        Args:
            output_file: 输出文件路径
        """
        if not os.path.exists(output_file):
            return
        
        backup_dir = os.path.join(os.path.dirname(output_file), 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{os.path.basename(output_file)}.{timestamp}.bak")
        
        # 复制文件
        shutil.copy2(output_file, backup_file)
        logger.info(f"创建备份文件: {backup_file}")
    
    def generate_config(self, proxies, template_config, output_file):
        """生成优化后的Clash配置文件
        
        Args:
            proxies: 代理节点列表
            template_config: 模板配置
            output_file: 输出文件路径
        """
        if not proxies:
            logger.warning("没有有效的代理节点，无法生成配置文件")
            return False
        
        # 创建备份
        if self.output_config.get('backup', True) and os.path.exists(output_file):
            self._create_backup(output_file)
        
        # 复制模板配置
        new_config = template_config.copy()
        
        # 更新代理节点
        new_config['proxies'] = proxies
        
        # 如果有代理组，更新代理组中的代理列表
        if 'proxy-groups' in new_config:
            for group in new_config['proxy-groups']:
                # 如果代理组使用除"select"和"url-test"之外的其他类型，跳过
                if group.get('type', '') not in ['select', 'url-test', 'fallback', 'load-balance']:
                    continue
                
                # 为代理组添加所有代理节点
                proxy_names = [proxy.get('name') for proxy in proxies]
                group['proxies'] = proxy_names
        
        # 添加元数据
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'metadata' not in new_config:
            new_config['metadata'] = {}
        
        new_config['metadata'].update({
            'updated': timestamp,
            'proxy_count': len(proxies),
            'generated_by': 'Clash Config Merger'
        })
        
        # 写入文件
        try:
            # 确保YAML可以处理典型的Clash配置格式
            class SafeDumper(yaml.SafeDumper):
                pass
            
            def represent_none(self, _):
                return self.represent_scalar('tag:yaml.org,2002:null', '')
            
            SafeDumper.add_representer(type(None), represent_none)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, default_flow_style=False, sort_keys=False, Dumper=SafeDumper, allow_unicode=True)
            
            logger.info(f"配置文件生成成功: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"生成配置文件时发生错误: {str(e)}")
            return False 