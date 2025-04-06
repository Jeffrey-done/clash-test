#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件抓取器 - 从GitHub、直接URL或本地文件获取Clash配置文件
"""

import logging
import aiohttp
import asyncio
import yaml
import os
from rich.progress import Progress
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

class GitHubFetcher:
    """配置文件抓取器，用于从GitHub或直接URL获取Clash配置文件"""
    
    def __init__(self, config):
        """初始化抓取器
        
        Args:
            config: 程序配置
        """
        self.config = config
        self.repositories = config.get('repositories', []) or []
        self.yaml_urls = config.get('yaml_urls', []) or []
        self.local_files = config.get('local_files', []) or []
        self.proxy = None
        
        # 如果配置了HTTP代理
        proxy_config = config.get('proxy', {})
        if proxy_config.get('enable', False):
            self.proxy = proxy_config.get('address')
            logger.info(f"使用HTTP代理: {self.proxy}")
            console.print(f"[yellow]使用HTTP代理: {self.proxy}[/yellow]")
    
    async def fetch_content(self, session, url):
        """从URL获取文件内容
        
        Args:
            session: aiohttp会话
            url: 文件URL
            
        Returns:
            文件内容
        """
        try:
            # 显示当前请求的URL
            logger.debug(f"正在请求: {url}")
            
            # 发送请求，如果有代理则使用代理
            kwargs = {}
            if self.proxy:
                kwargs['proxy'] = self.proxy
                
            async with session.get(url, **kwargs) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"成功获取配置文件: {url}")
                    return content
                else:
                    logger.warning(f"获取配置文件失败: {url}, 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取配置文件时发生错误: {url}, 错误: {str(e)}")
            return None
    
    def read_local_file(self, file_path):
        """读取本地文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            logger.info(f"正在读取本地文件: {file_path}")
            if not os.path.exists(file_path):
                logger.warning(f"本地文件不存在: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            logger.info(f"成功读取本地文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"读取本地文件时发生错误: {file_path}, 错误: {str(e)}")
            return None
    
    async def load_local_file(self, file_path, progress, task_id):
        """加载本地配置文件
        
        Args:
            file_path: 文件路径
            progress: 进度条
            task_id: 任务ID
            
        Returns:
            配置数据
        """
        content = self.read_local_file(file_path)
        if content:
            try:
                # 尝试解析YAML内容
                config_data = yaml.safe_load(content)
                if self._is_valid_clash_config(config_data):
                    logger.info(f"成功解析本地配置文件: {file_path}")
                    if progress and task_id:
                        progress.update(task_id, advance=1)
                    return config_data
                else:
                    logger.warning(f"无效的本地Clash配置文件: {file_path}")
            except Exception as e:
                logger.error(f"解析本地配置文件失败: {file_path}, 错误: {str(e)}")
        
        if progress and task_id:
            progress.update(task_id, advance=1)
        return None
    
    async def fetch_github_content(self, session, owner, repo, path):
        """从GitHub获取文件内容
        
        Args:
            session: aiohttp会话
            owner: 仓库拥有者
            repo: 仓库名称
            path: 文件路径
            
        Returns:
            文件内容
        """
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}"
        return await self.fetch_content(session, url)
    
    async def fetch_repository_configs(self, session, repository, progress, task_id):
        """从仓库获取所有配置文件
        
        Args:
            session: aiohttp会话
            repository: 仓库信息
            progress: 进度条
            task_id: 任务ID
            
        Returns:
            配置文件列表
        """
        owner = repository.get('owner')
        repo = repository.get('repo')
        paths = repository.get('paths', [])
        
        configs = []
        for path in paths:
            content = await self.fetch_github_content(session, owner, repo, path)
            if content:
                try:
                    # 尝试解析YAML内容
                    config_data = yaml.safe_load(content)
                    if self._is_valid_clash_config(config_data):
                        configs.append(config_data)
                        logger.info(f"成功解析配置文件: {owner}/{repo}/{path}")
                    else:
                        logger.warning(f"无效的Clash配置文件: {owner}/{repo}/{path}")
                except Exception as e:
                    logger.error(f"解析配置文件失败: {owner}/{repo}/{path}, 错误: {str(e)}")
        
        if progress and task_id:
            progress.update(task_id, advance=1)
        return configs
    
    async def fetch_yaml_url(self, session, url, progress, task_id):
        """从URL获取YAML配置
        
        Args:
            session: aiohttp会话
            url: YAML文件URL
            progress: 进度条
            task_id: 任务ID
            
        Returns:
            配置文件
        """
        content = await self.fetch_content(session, url)
        if content:
            try:
                # 尝试解析YAML内容
                config_data = yaml.safe_load(content)
                if self._is_valid_clash_config(config_data):
                    logger.info(f"成功解析配置文件: {url}")
                    if progress and task_id:
                        progress.update(task_id, advance=1)
                    return config_data
                else:
                    logger.warning(f"无效的Clash配置文件: {url}")
            except Exception as e:
                logger.error(f"解析配置文件失败: {url}, 错误: {str(e)}")
        
        if progress and task_id:
            progress.update(task_id, advance=1)
        return None
    
    def _is_valid_clash_config(self, config):
        """检查是否是有效的Clash配置
        
        Args:
            config: 配置数据
            
        Returns:
            是否是有效的Clash配置
        """
        # 简单检查，判断是否包含必要的字段
        return (isinstance(config, dict) and 
                ('proxies' in config or 'proxy-providers' in config or 'proxy-groups' in config))
    
    async def fetch_all_configs(self, progress, task_id):
        """获取所有配置文件
        
        Args:
            progress: 进度条
            task_id: 任务ID
            
        Returns:
            所有配置文件列表
        """
        # 设置连接器，SSL验证和超时
        connector = aiohttp.TCPConnector(ssl=False, limit=10)  # 增加连接数限制
        timeout = aiohttp.ClientTimeout(total=60)  # 增加超时时间到60秒
        
        # 准备session参数
        session_kwargs = {
            'connector': connector,
            'timeout': timeout
        }
        
        all_configs = []
        
        # 先加载本地文件
        if self.local_files:
            console.print("[yellow]正在加载本地配置文件...[/yellow]")
            local_tasks = []
            for file_path in self.local_files:
                task = self.load_local_file(file_path, progress, task_id)
                local_tasks.append(task)
            
            local_results = await asyncio.gather(*local_tasks, return_exceptions=True)
            for result in local_results:
                if isinstance(result, dict):
                    all_configs.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"加载本地配置文件时发生错误: {str(result)}")
        
        # 然后获取远程配置
        # 创建会话
        async with aiohttp.ClientSession(**session_kwargs) as session:
            # 如果配置了代理，在请求时使用代理
            proxy_kwarg = {}
            if self.proxy:
                proxy_kwarg['proxy'] = self.proxy
            
            tasks = []
            
            # 添加GitHub仓库任务
            for repo in self.repositories:
                task = self.fetch_repository_configs(session, repo, progress, task_id)
                tasks.append(task)
            
            # 添加YAML URL任务
            for url in self.yaml_urls:
                task = self.fetch_yaml_url(session, url, progress, task_id)
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤出成功的结果
            for result in results:
                if isinstance(result, list):
                    all_configs.extend(result)
                elif isinstance(result, dict):
                    all_configs.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"获取配置文件时发生错误: {str(result)}")
        
        return all_configs 