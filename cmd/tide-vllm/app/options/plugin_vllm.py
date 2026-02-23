#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: vLLM - tide-vllm 的 vLLM 客户端安装

VLLMServerManager / VLLMConfig / parse_vllm_config 等通用逻辑已下沉到
peek.plugins.vllm，本文件只负责 client 创建 + provider 注册。
"""

import logging
from typing import Optional

from peek.plugins.vllm import (
    VLLMConfig,
    VLLMServerManager,
    install_vllm as _install_vllm,
    uninstall_vllm,
    get_vllm_server_manager,
)

logger = logging.getLogger(__name__)


async def _register_client(config: VLLMConfig, server_manager: Optional[VLLMServerManager]) -> None:
    """创建 vLLM 客户端并注册到 tide-vllm 的 provider"""
    from tide.provider import get_provider
    from peek.ai.vllm import VLLMClient

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

    provider = get_provider()
    provider.set_vllm_client(client)
    provider.set_vllm_config(config)
    if server_manager:
        provider.set_vllm_server_manager(server_manager)


async def install_vllm(config: Optional[VLLMConfig]):
    """安装 vLLM 客户端（以及可选的 vLLM server）"""
    await _install_vllm(config, register_client=_register_client)