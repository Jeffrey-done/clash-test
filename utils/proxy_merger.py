#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理合并器 - 合并和去重Clash配置中的代理节点
"""

import logging
import hashlib
import json
import re
import time
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

class ProxyMerger:
    """代理合并器，用于合并和去重Clash配置中的代理节点"""
    
    def __init__(self):
        """初始化代理合并器"""
        # 支持的代理类型
        self.supported_types = [
            'ss', 'ssr', 'vmess', 'trojan', 'socks5', 
            'http', 'snell', 'socks5-tls', 'vless'
        ]
        
        # 必需字段映射
        self.required_fields = {
            'ss': ['type', 'server', 'port', 'cipher'],
            'ssr': ['type', 'server', 'port', 'cipher', 'obfs', 'protocol'],
            'vmess': ['type', 'server', 'port', 'uuid'],
            'trojan': ['type', 'server', 'port', 'password'],
            'socks5': ['type', 'server', 'port'],
            'http': ['type', 'server', 'port'],
            'snell': ['type', 'server', 'port', 'psk'],
            'vless': ['type', 'server', 'port', 'uuid']
        }
    
    def merge_proxies(self, configs):
        """合并多个配置中的代理节点
        
        Args:
            configs: 配置列表
            
        Returns:
            合并后的代理节点列表，和第一个有效配置（用于保留结构）
        """
        if not configs:
            logger.warning("没有找到有效的配置文件")
            return [], {}
        
        all_proxies = []
        first_config = None
        total_invalid = 0
        
        for config in configs:
            try:
                # 保存第一个有效配置
                if first_config is None and isinstance(config, dict):
                    first_config = config
                
                # 提取代理节点
                if not isinstance(config, dict):
                    logger.warning(f"无效的配置格式: {type(config)}")
                    continue
                    
                proxies = config.get('proxies', [])
                if not proxies:
                    logger.warning("配置中没有找到代理节点")
                    continue
                
                # 过滤有效的代理节点
                valid_proxies = []
                for proxy in proxies:
                    if self._is_valid_proxy(proxy):
                        valid_proxies.append(proxy)
                    else:
                        total_invalid += 1
                
                logger.info(f"从配置中提取了 {len(valid_proxies)} 个有效代理节点 (忽略 {len(proxies) - len(valid_proxies)} 个无效节点)")
                all_proxies.extend(valid_proxies)
            except Exception as e:
                logger.error(f"处理配置时发生错误: {str(e)}")
        
        # 确保有第一个有效配置作为模板
        if first_config is None and all_proxies:
            # 如果没有找到有效的完整配置，但有代理节点，则创建一个最小配置
            first_config = {
                'port': 7890,
                'socks-port': 7891,
                'allow-lan': True,
                'mode': 'rule',
                'log-level': 'info',
                'external-controller': '127.0.0.1:9090',
                'proxies': []
            }
            logger.warning("未找到有效的完整配置，将使用默认配置模板")
        
        logger.info(f"合并后共有 {len(all_proxies)} 个代理节点 (总共忽略 {total_invalid} 个无效节点)")
        return all_proxies, first_config
    
    def _is_valid_proxy(self, proxy):
        """检查代理节点是否有效
        
        Args:
            proxy: 代理节点
            
        Returns:
            是否有效
        """
        if not isinstance(proxy, dict):
            return False
            
        # 检查类型
        proxy_type = proxy.get('type', '').lower()
        if proxy_type not in self.supported_types:
            return False
            
        # 检查必需字段
        required = self.required_fields.get(proxy_type, [])
        for field in required:
            if field not in proxy:
                return False
                
        # 检查名称
        name = proxy.get('name', '')
        if not name:
            return False
            
        # 检查服务器地址和端口
        server = proxy.get('server', '')
        port = proxy.get('port', 0)
        
        if not server or not self._is_valid_server_address(server):
            return False
            
        if not isinstance(port, int) or port <= 0 or port > 65535:
            return False
            
        return True
    
    def _is_valid_server_address(self, server):
        """检查服务器地址是否有效
        
        Args:
            server: 服务器地址
            
        Returns:
            是否有效
        """
        # 检查是否为IP地址
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        
        return bool(re.match(ip_pattern, server) or re.match(domain_pattern, server))
    
    def _generate_proxy_hash(self, proxy):
        """为代理节点生成哈希值，用于去重
        
        Args:
            proxy: 代理节点
            
        Returns:
            代理节点的哈希值
        """
        # 复制代理字典，移除不影响节点唯一性的字段
        proxy_copy = proxy.copy()
        proxy_copy.pop('name', None)  # 名称可能会被修改，但节点本身可能相同
        proxy_copy.pop('udp', None)   # UDP支持不影响节点唯一性
        proxy_copy.pop('tfo', None)   # TCP Fast Open不影响节点唯一性
        
        # 将代理信息转换为JSON字符串，然后生成哈希
        try:
            proxy_str = json.dumps(proxy_copy, sort_keys=True)
            return hashlib.md5(proxy_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"生成代理哈希时发生错误: {str(e)}")
            # 返回一个随机哈希，确保不会被当作重复节点
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def remove_duplicates(self, proxies):
        """移除重复的代理节点
        
        Args:
            proxies: 代理节点列表
            
        Returns:
            去重后的代理节点列表
        """
        unique_proxies = {}
        duplicate_count = 0
        error_count = 0
        
        for proxy in proxies:
            try:
                proxy_hash = self._generate_proxy_hash(proxy)
                
                # 如果这个哈希值还没有出现过，就添加到结果中
                if proxy_hash not in unique_proxies:
                    unique_proxies[proxy_hash] = proxy
                else:
                    duplicate_count += 1
            except Exception as e:
                logger.error(f"处理代理节点时发生错误: {str(e)}")
                error_count += 1
        
        if error_count > 0:
            logger.warning(f"去重过程中有 {error_count} 个节点处理失败")
            
        logger.info(f"去重: 移除了 {duplicate_count} 个重复节点")
        return list(unique_proxies.values()) 