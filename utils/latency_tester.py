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
        self.timeout_ms = latency_config.get('timeout', 5000) / 1000  # 转换为秒
        self.concurrent_tests = latency_config.get('concurrent_tests', 50)
        self.retry_count = latency_config.get('retry_count', 2)
        
        # 增加一个随机延迟，避免同时大量连接导致网络拥堵
        self.max_random_delay = 0.5  # 最大随机延迟秒数
    
    async def test_proxy(self, proxy):
        """测试单个代理节点的延迟
        
        Args:
            proxy: 代理节点
            
        Returns:
            (代理节点, 延迟毫秒数) 元组，如果节点无效则延迟为 -1
        """
        # 随机延迟开始测试，减轻突发连接压力
        await asyncio.sleep(random.uniform(0, self.max_random_delay))
        
        server = proxy.get('server')
        port = proxy.get('port')
        
        if not server or not port:
            logger.warning(f"代理节点缺少服务器或端口信息: {proxy.get('name', '未命名')}")
            return proxy, -1
        
        # 尝试多次连接，取最小延迟
        min_latency = float('inf')
        success = False
        sock = None
        
        for attempt in range(self.retry_count):
            try:
                start_time = time.time()
                
                # 确定IP地址类型 (IPv4 或 IPv6)
                addr_info = None
                try:
                    # 尝试解析地址
                    addr_info = socket.getaddrinfo(server, int(port), socket.AF_UNSPEC, socket.SOCK_STREAM)
                except socket.gaierror:
                    logger.debug(f"无法解析地址: {server}")
                    continue
                
                if not addr_info:
                    continue
                
                # 使用第一个地址信息
                family, socktype, proto, _, addr = addr_info[0]
                
                # 创建适当类型的socket
                sock = socket.socket(family, socktype, proto)
                sock.settimeout(self.timeout_ms)
                
                # 连接
                await asyncio.get_event_loop().sock_connect(sock, addr)
                
                latency = (time.time() - start_time) * 1000  # 转换为毫秒
                min_latency = min(min_latency, latency)
                success = True
                
                # 关闭socket
                sock.close()
                sock = None
                
                # 如果已经成功，就不需要再重试了
                break
                
            except (socket.timeout, socket.error, OSError) as e:
                logger.debug(f"连接失败 (尝试 {attempt+1}/{self.retry_count}): {proxy.get('name', '未命名')}, 错误: {str(e)}")
                await asyncio.sleep(0.5)  # 失败后短暂等待再重试
                continue
            except Exception as e:
                logger.error(f"测试节点时发生未知错误: {proxy.get('name', '未命名')}, 错误: {str(e)}")
                break
            finally:
                # 确保socket被关闭
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
        
        if success:
            logger.debug(f"节点 {proxy.get('name', '未命名')} 延迟: {min_latency:.2f}ms")
            # 将延迟添加到代理信息中
            proxy['latency'] = round(min_latency, 2)
            return proxy, min_latency
        else:
            logger.debug(f"节点 {proxy.get('name', '未命名')} 连接失败")
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
                
            # 每批次测试后稍微暂停，避免连续大量请求
            if i < len(batches) - 1:  # 如果不是最后一批
                await asyncio.sleep(0.5)
        
        # 按延迟排序
        valid_proxies.sort(key=lambda x: x.get('latency', float('inf')))
        
        invalid_count = len(proxies) - len(valid_proxies)
        logger.info(f"延迟测试完成: {len(valid_proxies)} 个有效节点, {invalid_count} 个无效节点")
        
        return valid_proxies 