#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Server Run Options - vLLM 服务配置选项
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class WebConfig:
    """Web 服务器配置。"""

    bind_address: Dict[str, Any] = field(default_factory=lambda: {"port": 10002})
    grpc: Dict[str, Any] = field(default_factory=dict)
    http: Dict[str, Any] = field(default_factory=dict)
    debug: Dict[str, Any] = field(default_factory=dict)
    open_telemetry: Dict[str, Any] = field(default_factory=dict)
    qps_limit: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogConfig:
    """日志配置。"""

    formatter: str = "glog"
    level: str = "debug"
    filepath: str = "./log"
    max_age: str = "604800s"
    max_count: int = 200
    rotate_interval: str = "3600s"
    rotate_size: int = 104857600
    report_caller: bool = True
    redirect: str = "stdout"


@dataclass
class VLLMConfig:
    """vLLM 服务配置。"""
    
    # vLLM 服务器配置
    enabled: bool = False
    host: str = "localhost"
    port: int = 8000
    api_key: str = ""
    
    # 是否自动启动 vLLM server（设为 True 则在服务启动时自动启动 vLLM）
    auto_start: bool = False
    
    # 模型配置
    model_name: str = "Qwen/Qwen2.5-7B-Instruct"  # served model name
    model_path: str = "Qwen/Qwen2.5-7B-Instruct"  # 模型路径（本地路径或 HuggingFace model id）
    
    # 生成参数
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    
    # 请求超时配置
    timeout: int = 60
    
    # vLLM server 启动参数（仅当 auto_start=True 时有效）
    gpu_memory_utilization: float = 0.9      # GPU 显存使用率
    tensor_parallel_size: int = 1            # 张量并行大小（多 GPU）
    max_num_seqs: int = 256                  # 最大并发序列数
    max_num_batched_tokens: int = 8192       # 最大批处理 token 数
    max_model_len: int = 4096                # 模型最大上下文长度
    dtype: str = "auto"                      # 数据类型: auto, float16, bfloat16, float32
    startup_timeout: int = 600               # vLLM server 启动超时时间（秒）
    enable_prefix_caching: bool = True       # 启用前缀缓存
    enable_chunked_prefill: bool = True      # 启用分块预填充


@dataclass
class ServerRunOptions:
    """服务器运行选项。"""

    config_file: str
    config: Dict[str, Any] = field(default_factory=dict)
    web_config: Optional[WebConfig] = None
    log_config: Optional[LogConfig] = None
    vllm_config: Optional[VLLMConfig] = None

    def __post_init__(self):
        """从文件加载配置。"""
        self._load_config()

    def _load_config(self):
        """从 YAML 文件加载配置。"""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

            # 解析子配置
            self.web_config = self._parse_web_config(self.config.get("web", {}))
            self.log_config = self._parse_log_config(self.config.get("log", {}))
            self.vllm_config = self._parse_vllm_config(self.config.get("vllm", {}))
        else:
            logger.warning(f"配置文件未找到: {config_path}")
            self.web_config = WebConfig()
            self.log_config = LogConfig()
            self.vllm_config = VLLMConfig()

    def _parse_web_config(self, data: Dict[str, Any]) -> WebConfig:
        """解析 Web 配置。"""
        return WebConfig(
            bind_address=data.get("bind_address", {"port": 10002}),
            grpc=data.get("grpc", {}),
            http=data.get("http", {}),
            debug=data.get("debug", {}),
            open_telemetry=data.get("open_telemetry", {}),
            qps_limit=data.get("qps_limit", {}),
        )

    def _parse_log_config(self, data: Dict[str, Any]) -> LogConfig:
        """解析日志配置。"""
        return LogConfig(
            formatter=data.get("formatter", "glog"),
            level=data.get("level", "debug"),
            filepath=data.get("filepath", "./log"),
            max_age=data.get("max_age", "604800s"),
            max_count=data.get("max_count", 200),
            rotate_interval=data.get("rotate_interval", "3600s"),
            rotate_size=data.get("rotate_size", 104857600),
            report_caller=data.get("report_caller", True),
            redirect=data.get("redirect", "stdout"),
        )

    def _parse_vllm_config(self, data: Dict[str, Any]) -> VLLMConfig:
        """解析 vLLM 配置。"""
        return VLLMConfig(
            enabled=data.get("enabled", False),
            host=data.get("host", "localhost"),
            port=data.get("port", 8000),
            api_key=data.get("api_key", ""),
            auto_start=data.get("auto_start", False),
            model_name=data.get("model_name", "Qwen/Qwen2.5-7B-Instruct"),
            model_path=data.get("model_path", "Qwen/Qwen2.5-7B-Instruct"),
            max_tokens=data.get("max_tokens", 2048),
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 0.9),
            timeout=data.get("timeout", 60),
            # vLLM server 启动参数
            gpu_memory_utilization=data.get("gpu_memory_utilization", 0.9),
            tensor_parallel_size=data.get("tensor_parallel_size", 1),
            max_num_seqs=data.get("max_num_seqs", 256),
            max_num_batched_tokens=data.get("max_num_batched_tokens", 8192),
            max_model_len=data.get("max_model_len", 4096),
            dtype=data.get("dtype", "auto"),
            startup_timeout=data.get("startup_timeout", 600),
            enable_prefix_caching=data.get("enable_prefix_caching", True),
            enable_chunked_prefill=data.get("enable_chunked_prefill", True),
        )

    def complete(self) -> "CompletedServerRunOptions":
        """完成设置默认 ServerRunOptions。"""
        return CompletedServerRunOptions(self)


class CompletedServerRunOptions:
    """已完成的服务器运行选项。

    一个包装器，强制在调用 run 之前调用 complete()。
    """

    def __init__(self, options: ServerRunOptions):
        self._options = options

    @property
    def options(self) -> ServerRunOptions:
        """获取底层选项。"""
        return self._options

    async def run(self):
        """运行服务器。"""
        from tide import __version__

        logger.info(f"正在启动 tide-vllm 版本 {__version__}")

        # 按顺序安装插件
        self._install_logs()
        self._install_config()

        # 创建 Web 服务器
        web_server = await self._create_web_server()

        # 安装 vLLM 客户端
        await self._install_vllm()

        # 安装 Web 处理器
        self._install_web_handler(web_server)

        # 运行服务器
        if hasattr(web_server, 'run_async'):
            await web_server.run_async()
        else:
            await web_server.run()

    def _install_logs(self):
        """安装日志配置。"""
        from .plugin_logs import install_logs

        install_logs(self._options.log_config)

    def _install_config(self):
        """将配置安装到 provider。"""
        from .plugin_config import install_config

        install_config(self._options.config)

    async def _create_web_server(self):
        """创建并配置 Web 服务器。"""
        from tide.plugins.webserver import create_web_server

        return await create_web_server(self._options.web_config)

    async def _install_vllm(self):
        """安装 vLLM 客户端。"""
        from .plugin_vllm import install_vllm

        await install_vllm(self._options.vllm_config)

    def _install_web_handler(self, web_server):
        """安装 Web 处理器。"""
        from .plugin_web_handler import install_web_handler

        install_web_handler(web_server)