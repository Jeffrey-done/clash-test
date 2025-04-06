#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
延迟测试器 - 测试代理节点的延迟并移除失效节点
"""

import logging
import asyncio
import socket
import time
import random
from rich.progress import Progress, TaskID
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

class LatencyTester:
    """延迟测试器，用于测试代理节点的延迟并移除失效节点"""
    
    def __init__(self, config):
        """初始化延迟测试器
        
        Args:
            config: 程序配置
        """
        self.config = config
        latency_config = config.get('latency_test', {}) or {}
        self.timeout_ms = latency_config.get('timeout', 2000)  # 降低默认值为2000ms
        self.concurrent_tests = latency_config.get('concurrent_tests', 20)  # 降低默认值为20
        self.retry_count = latency_config.get('retry_count', 1)
        self.batch_interval = latency_config.get('batch_interval', 1)  # 增加批次间隔默认为1秒
        self.max_nodes = latency_config.get('max_nodes', 300)  # 增加最大节点数限制
        
        # 增加一个随机延迟，避免同时大量连接导致网络拥堵
        random.seed(time.time())
    
    async def test_proxy(self, proxy):
        """测试单个代理节点的延迟
        
        Args:
            proxy: 代理节点字典
            
        Returns:
            如果连接成功，返回(proxy, latency)，否则返回(proxy, -1)
        """
        # 随机延迟开始测试，减轻突发连接压力
        await asyncio.sleep(random.uniform(0, 0.5))
        
        server = proxy.get('server')
        port = proxy.get('port')
        
        if not self._is_valid_address(server) or not port:
            logger.warning(f"无效的服务器地址或端口: {server}:{port}")
            return proxy, -1
        
        # 设置超时时间更短，避免卡死
        timeout_seconds = min(self.timeout_ms / 1000, 2.0)  # 最大2秒
        
        latency = -1  # 默认为-1表示失败
        
        # 尝试解析域名，获取地址信息
        try:
            # 尝试获取地址信息
            addrinfo = socket.getaddrinfo(server, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            
            # 我们将尝试第一个可用的地址
            for retry in range(self.retry_count):
                for family, socktype, proto, canonname, sockaddr in addrinfo:
                    try:
                        # 创建适当类型的socket
                        sock = socket.socket(family, socktype, proto)
                        sock.settimeout(timeout_seconds)
                        
                        # 连接
                        start_time = time.time()
                        sock.connect(sockaddr)
                        end_time = time.time()
                        
                        # 计算延迟（毫秒）
                        latency = int((end_time - start_time) * 1000)
                        
                        # 更新代理信息
                        proxy['latency'] = latency
                        
                        # 关闭连接
                        sock.close()
                        
                        # 延迟测试成功，返回
                        return proxy, latency
                    except (socket.timeout, ConnectionRefusedError, OSError) as e:
                        if sock:
                            sock.close()
                        # 记录失败，尝试下一个地址
                        continue
            
            # 如果所有地址都失败
            return proxy, -1
            
        except (socket.gaierror, socket.error) as e:
            # 无法解析域名或其他错误
            logger.debug(f"无法连接到服务器 {server}:{port} - {str(e)}")
            return proxy, -1
        except Exception as e:
            # 捕获所有其他异常
            logger.debug(f"测试代理时发生错误 {server}:{port} - {str(e)}")
            return proxy, -1
    
    async def test_batch(self, proxies, progress=None, task_id=None):
        """测试一批代理节点
        
        Args:
            proxies: 代理节点列表
            progress: 进度条
            task_id: 任务ID
            
        Returns:
            有效的代理节点列表
        """
        if not proxies:
            return []
            
        tasks = []
        for proxy in proxies:
            task = asyncio.create_task(self.test_proxy(proxy))
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"批量测试节点时发生错误: {str(e)}")
            results = []
        
        # 更新进度
        if progress and task_id:
            progress.update(task_id, advance=len(proxies))
        
        # 过滤出有效的节点和处理异常
        valid_proxies = []
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                proxy, latency = result
                if latency > 0:  # 延迟大于0表示节点有效
                    valid_proxies.append(proxy)
            elif isinstance(result, Exception):
                logger.error(f"测试节点时发生错误: {str(result)}")
        
        return valid_proxies
    
    async def test_all_proxies(self, proxies, task_status=None):
        """测试所有代理节点
        
        Args:
            proxies: 代理节点列表
            task_status: 任务状态字典，用于检查是否应该中断测试
            
        Returns:
            有效的代理节点列表，按延迟排序
        """
        if not proxies:
            logger.warning("没有代理节点可供测试")
            return []
        
        # 使用我们自己的进度显示，而不是嵌套的Progress
        console.print("[cyan]正在测试节点延迟...[/cyan]")
        
        # 检查是否超过最大节点数
        if len(proxies) > self.max_nodes:
            logger.warning(f"节点数量({len(proxies)})超过最大限制({self.max_nodes})，将随机选择{self.max_nodes}个节点进行测试")
            console.print(f"[yellow]节点数量过多，将只测试{self.max_nodes}个节点[/yellow]")
            random.shuffle(proxies)
            proxies = proxies[:self.max_nodes]
            
        # 分批测试，避免并发太多
        batches = [proxies[i:i+self.concurrent_tests] for i in range(0, len(proxies), self.concurrent_tests)]
        valid_proxies = []
        
        for i, batch in enumerate(batches):
            # 检查任务是否被取消
            if task_status and not task_status.get('running', True):
                logger.info("测试任务被中断，返回已测试的节点")
                console.print("[yellow]测试任务被中断，返回已测试的节点[/yellow]")
                break
                
            logger.info(f"测试批次 {i+1}/{len(batches)}，包含 {len(batch)} 个节点")
            console.print(f"[cyan]测试批次 {i+1}/{len(batches)}，共 {len(batch)} 个节点[/cyan]")
            
            # 测试这一批节点
            batch_results = await self.test_batch(batch)
            valid_proxies.extend(batch_results)
            
            # 显示进度
            console.print(f"[green]批次 {i+1} 完成，有效节点: {len(batch_results)}/{len(batch)}[/green]")
            
            # 更新任务进度（如果提供了任务状态）
            if task_status:
                progress_value = int(60 + (i+1) / len(batches) * 30)  # 60%-90%之间更新进度
                task_status['progress'] = min(progress_value, 90)
                
            # 每批次测试后休眠指定时间，避免连续大量请求
            if i < len(batches) - 1:  # 如果不是最后一批
                logger.info(f"等待 {self.batch_interval} 秒后开始下一批测试")
                await asyncio.sleep(self.batch_interval)
        
        # 按延迟排序
        valid_proxies.sort(key=lambda x: x.get('latency', float('inf')))
        
        invalid_count = len(proxies) - len(valid_proxies)
        logger.info(f"延迟测试完成: {len(valid_proxies)} 个有效节点, {invalid_count} 个无效节点")
        
        return valid_proxies 