# -*- coding: utf-8 -*-
"""vLLM Chat Repository - tide-vllm 的仓库适配层

核心实现已下沉到 peek.ai.vllm.chat.vllm_repository。
本模块仅提供与 tide-vllm Provider 的桥接。
"""

from peek.ai.vllm.chat.vllm_repository import VLLMChatRepository as _BaseVLLMChatRepository
from tide.provider import get_provider as global_provider


def _get_client():
    """从 tide-vllm provider 获取 vLLM 客户端"""
    provider = global_provider()
    client = provider.get_vllm_client()
    if client is None:
        raise RuntimeError("vLLM 客户端未初始化，请检查配置")
    return client


def _get_server_manager():
    """从 tide-vllm provider 获取 vLLM server manager"""
    provider = global_provider()
    return provider.get_vllm_server_manager()


class VLLMChatRepository(_BaseVLLMChatRepository):
    """tide-vllm 专用的 VLLMChatRepository
    
    自动从 tide-vllm 的 global_provider 获取依赖。
    """
    
    def __init__(self):
        super().__init__(
            get_client=_get_client,
            get_server_manager=_get_server_manager,
        )