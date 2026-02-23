#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");

Server Run Options - vLLM 服务配置选项
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from tide.plugins.base_options import (
    BaseCompletedOptions,
    BaseServerRunOptions,
    LogConfig,
    WebConfig,
)

logger = logging.getLogger(__name__)


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
    
    # 多模态处理参数
    mm_processor_kwargs: Optional[Dict[str, Any]] = None  # 多模态处理器参数（如视频帧采样配置）
    media_io_kwargs: Optional[Dict[str, Any]] = None      # 媒体IO参数（如视频帧数控制）

    # 视频场景审核特有配置
    logprobs: bool = True                    # 是否返回 logprobs
    top_logprobs: int = 10                   # 返回 top-k 个 logprobs
    seed: int = 42                           # 随机种子
    scene_cls_threshold: float = 0.1         # 场景分类阈值
    max_concurrent_requests: int = 4         # 最大并发请求数

    # 视频解码配置
    video_decode: Optional[Dict[str, Any]] = None  # 视频解码配置


class ServerRunOptions(BaseServerRunOptions):
    """vLLM 服务器运行选项。"""

    default_port = 10002

    def __init__(self, config_file: str):
        self.vllm_config: Optional[VLLMConfig] = None
        super().__init__(config_file)

    def _load_business_config(self):
        """加载 vLLM 业务配置。"""
        self.vllm_config = self._parse_vllm_config(self.config.get("vllm", {}))

    def _init_default_business_config(self):
        """初始化 vLLM 默认配置。"""
        self.vllm_config = VLLMConfig()

    def _parse_vllm_config(self, data: Dict[str, Any]) -> VLLMConfig:
        """解析 vLLM 配置。"""
        logger.info(
            f"解析 vLLM 配置: model_name={data.get('model_name', '未设置')}, "
            f"model_path={data.get('model_path', '未设置')}, "
            f"host={data.get('host', '未设置')}, "
            f"port={data.get('port', '未设置')}, "
            f"auto_start={data.get('auto_start', '未设置')}"
        )
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
            # 多模态处理参数
            mm_processor_kwargs=data.get("mm_processor_kwargs", None),
            media_io_kwargs=data.get("media_io_kwargs", None),
            # 视频场景审核特有配置
            logprobs=data.get("logprobs", True),
            top_logprobs=data.get("top_logprobs", 10),
            seed=data.get("seed", 42),
            scene_cls_threshold=data.get("scene_cls_threshold", 0.1),
            max_concurrent_requests=data.get("max_concurrent_requests", 4),
            # 视频解码配置
            video_decode=data.get("video_decode", None),
        )

    def complete(self) -> "CompletedServerRunOptions":
        """完成设置默认 ServerRunOptions。"""
        return CompletedServerRunOptions(self)


class CompletedServerRunOptions(BaseCompletedOptions):
    """vLLM 服务已完成的服务器运行选项。"""

    _service_name = "tide-vllm"

    def _install_config(self):
        """将配置安装到 provider。"""
        from pkg.tide_vllm.provider import global_provider

        provider = global_provider()
        provider.config = self._options.config
        logger.info(f"配置已安装: {list(self._options.config.keys())}")

    async def _install_business(self, web_server):
        """安装 vLLM 客户端。"""
        from .plugin_vllm import install_vllm

        await install_vllm(self._options.vllm_config)

    def _install_web_handler(self, web_server):
        """安装 Web 处理器。"""
        from .plugin_web_handler import install_web_handler

        install_web_handler(web_server)