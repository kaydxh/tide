#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: vLLM - vLLM 客户端与服务器管理插件

该插件用于：
1. 自动启动 vLLM server 进程（如果配置了 auto_start=True）
2. 初始化 vLLM 客户端，连接到 vLLM 服务器
"""

import asyncio
import atexit
import logging
import os
import signal
import subprocess
import time
from typing import Optional

import httpx

from .options import VLLMConfig

logger = logging.getLogger(__name__)


class VLLMServerManager:
    """vLLM Server 进程管理器
    
    负责启动、停止和监控 vLLM server 进程。
    参考 mmpayantifraudytllmserving 项目的 base_model.py 实现。
    """
    
    def __init__(self, config: VLLMConfig):
        """初始化 vLLM Server 管理器
        
        Args:
            config: vLLM 配置
        """
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.log_task: Optional[asyncio.Task] = None
        self._api_url = f"http://{config.host}:{config.port}/v1"
        
        # 注册退出清理
        atexit.register(self._cleanup_on_exit)
    
    def _cleanup_on_exit(self):
        """程序退出时清理 vLLM server 进程"""
        if self.process:
            logger.info("程序退出，停止 vLLM server...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception as e:
                logger.error(f"停止 vLLM server 时出错: {e}")
    
    async def start(self) -> None:
        """启动 vLLM server 进程"""
        if self.process is not None:
            logger.warning("vLLM server 已经在运行中")
            return
        
        # 构建 vLLM 启动命令
        cmd = self._build_vllm_command()
        
        logger.info(f"启动 vLLM server，命令: {' '.join(cmd)}")
        
        try:
            # 使用环境变量
            env = os.environ.copy()
            
            # 启动 vLLM 进程
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并 stderr 到 stdout
                universal_newlines=False,  # 使用 bytes 模式
                bufsize=0,  # 无缓冲，bytes 模式下不支持行缓冲
                preexec_fn=os.setsid,  # 创建新的进程组
            )
            
            logger.info(f"vLLM server 已启动，PID: {self.process.pid}")
            
            # 启动后台任务记录 vLLM 输出
            self.log_task = asyncio.create_task(self._log_vllm_output())
            
        except FileNotFoundError:
            # vllm 命令不存在
            logger.error(
                "vLLM 命令未找到！请确保已安装 vLLM：\n"
                "  pip install vllm\n"
                "或者设置 auto_start=false 并手动启动 vLLM server"
            )
            raise RuntimeError(
                "vLLM 命令未找到，请先安装 vLLM (pip install vllm) "
                "或设置 auto_start=false"
            )
        except Exception as e:
            logger.error(f"启动 vLLM server 失败: {e}", exc_info=True)
            raise RuntimeError(f"vLLM server 启动失败: {e}")
    
    def _build_vllm_command(self) -> list:
        """构建 vLLM 启动命令"""
        cmd = [
            "vllm",
            "serve",
            self.config.model_path,
            "--host", self.config.host,
            "--port", str(self.config.port),
            "--served-model-name", self.config.model_name,
            "--gpu-memory-utilization", str(self.config.gpu_memory_utilization),
            "--max-num-batched-tokens", str(self.config.max_num_batched_tokens),
            "--max-num-seqs", str(self.config.max_num_seqs),
            "--max-model-len", str(self.config.max_model_len),
            "--tensor-parallel-size", str(self.config.tensor_parallel_size),
        ]
        
        # 添加数据类型
        if self.config.dtype and self.config.dtype != "auto":
            cmd += ["--dtype", self.config.dtype]
        
        # 添加性能优化参数
        if self.config.enable_prefix_caching:
            cmd.append("--enable-prefix-caching")
        
        if self.config.enable_chunked_prefill:
            cmd.append("--enable-chunked-prefill")
        
        return cmd
    
    async def _log_vllm_output(self) -> None:
        """记录 vLLM server 输出"""
        if not self.process:
            return
        
        try:
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            transport, _ = await asyncio.get_event_loop().connect_read_pipe(
                lambda: protocol, self.process.stdout
            )
            
            try:
                while self.process and self.process.poll() is None:
                    try:
                        line = await asyncio.wait_for(reader.readline(), timeout=1.0)
                        if line:
                            line_str = line.decode("utf-8", errors="replace").strip()
                            logger.info(f"[vLLM] {line_str}")
                        else:
                            break
                    except asyncio.TimeoutError:
                        continue
                    except asyncio.CancelledError:
                        logger.debug("vLLM 日志读取任务已取消")
                        break
            finally:
                transport.close()
        except asyncio.CancelledError:
            logger.debug("vLLM 日志读取任务已取消")
        except Exception as e:
            logger.error(f"读取 vLLM 输出时出错: {e}", exc_info=True)
    
    async def wait_for_ready(self, timeout: Optional[int] = None) -> None:
        """等待 vLLM server 就绪
        
        Args:
            timeout: 超时时间（秒），默认使用配置的 startup_timeout
        """
        if timeout is None:
            timeout = self.config.startup_timeout
        
        logger.info(f"等待 vLLM server 就绪（超时: {timeout}s）...")
        logger.info("模型加载可能需要几分钟，请耐心等待...")
        
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < timeout:
            # 检查进程是否还在运行
            if self.process and self.process.poll() is not None:
                exit_code = self.process.returncode
                logger.error(f"vLLM server 进程意外终止，退出码: {exit_code}")
                raise RuntimeError(f"vLLM server 进程终止，退出码: {exit_code}")
            
            # 检查服务是否就绪
            try:
                if await self._check_server_ready():
                    elapsed = time.time() - start_time
                    logger.info(f"vLLM server 已就绪！耗时: {elapsed:.1f}s")
                    return
            except Exception as e:
                logger.debug(f"vLLM server 就绪检查失败: {e}")
            
            # 每 30 秒记录一次进度
            current_time = time.time()
            if current_time - last_log_time >= 30:
                elapsed = current_time - start_time
                remaining = timeout - elapsed
                logger.info(
                    f"仍在等待 vLLM server... "
                    f"（已等待 {elapsed:.0f}s，剩余 {remaining:.0f}s）"
                )
                last_log_time = current_time
            
            await asyncio.sleep(2)
        
        # 超时
        logger.error(f"vLLM server 启动超时（{timeout}s）")
        raise TimeoutError(f"vLLM server 未能在 {timeout}s 内就绪")
    
    async def _check_server_ready(self) -> bool:
        """检查 vLLM server 是否就绪
        
        通过调用 /v1/models 端点检查模型是否已加载
        
        Returns:
            bool: server 是否就绪
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._api_url}/models")
                if response.status_code == 200:
                    data = response.json()
                    model_names = [model["id"] for model in data.get("data", [])]
                    is_ready = self.config.model_name in model_names
                    if not is_ready:
                        logger.debug(
                            f"模型 {self.config.model_name} 尚未就绪，"
                            f"当前可用模型: {model_names}"
                        )
                    return is_ready
                else:
                    logger.debug(f"vLLM server 返回状态码: {response.status_code}")
                    return False
        except Exception as e:
            logger.debug(f"检查 vLLM server 就绪状态失败: {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查
        
        Returns:
            bool: server 是否健康
        """
        # 检查进程是否还在运行
        if self.process and self.process.poll() is not None:
            logger.warning(f"vLLM 进程已终止，退出码: {self.process.returncode}")
            return False
        
        return await self._check_server_ready()
    
    async def stop(self) -> None:
        """停止 vLLM server 进程"""
        if self.process is None:
            return
        
        logger.info("正在停止 vLLM server...")
        
        # 取消日志任务
        if self.log_task:
            self.log_task.cancel()
            self.log_task = None
        
        try:
            # 发送 SIGTERM 信号到进程组
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            
            # 等待优雅关闭
            try:
                self.process.wait(timeout=10)
                logger.info("vLLM server 已优雅停止")
            except subprocess.TimeoutExpired:
                # 强制终止
                logger.warning("vLLM server 未能优雅停止，强制终止...")
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()
                logger.info("vLLM server 已强制终止")
        except Exception as e:
            logger.error(f"停止 vLLM server 时出错: {e}", exc_info=True)
        finally:
            self.process = None


# 全局 vLLM server 管理器实例
_vllm_server_manager: Optional[VLLMServerManager] = None


def get_vllm_server_manager() -> Optional[VLLMServerManager]:
    """获取全局 vLLM server 管理器实例"""
    return _vllm_server_manager


async def install_vllm(config: Optional[VLLMConfig]):
    """安装 vLLM 客户端（以及可选的 vLLM server）。
    
    1. 如果配置了 auto_start=True，则先启动 vLLM server
    2. 初始化 vLLM 客户端并连接到 vLLM 服务器
    """
    global _vllm_server_manager
    
    if config is None or not config.enabled:
        logger.info("vLLM 客户端未启用")
        return

    try:
        # 如果配置了自动启动，先启动 vLLM server
        if config.auto_start:
            logger.info("配置了 auto_start=True，正在启动 vLLM server...")
            _vllm_server_manager = VLLMServerManager(config)
            await _vllm_server_manager.start()
            await _vllm_server_manager.wait_for_ready()
        
        from pkg.tide_vllm.provider import global_provider
        from pkg.tide_vllm.infrastructure.vllm import VLLMClient

        # 创建 vLLM 客户端
        client = VLLMClient(
            host=config.host,
            port=config.port,
            api_key=config.api_key,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            timeout=config.timeout,
        )

        # 注册到全局 provider
        provider = global_provider()
        provider.vllm_client = client
        if _vllm_server_manager:
            provider.vllm_server_manager = _vllm_server_manager

        logger.info(
            f"vLLM 客户端已安装: host={config.host}, "
            f"port={config.port}, model={config.model_name}, "
            f"auto_start={config.auto_start}"
        )

    except ImportError as e:
        logger.error(f"导入 vLLM 模块失败: {e}")
        raise
    except Exception as e:
        logger.error(f"安装 vLLM 客户端失败: {e}")
        raise


async def uninstall_vllm():
    """卸载 vLLM（停止 server 进程）"""
    global _vllm_server_manager
    
    if _vllm_server_manager:
        await _vllm_server_manager.stop()
        _vllm_server_manager = None
        logger.info("vLLM server 已停止")