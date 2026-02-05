# -*- coding: utf-8 -*-
"""Provider - 全局服务提供者"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import threading


@dataclass
class Provider:
    """全局服务提供者。
    
    用于存储和访问全局配置和服务实例。
    """
    config: Dict[str, Any] = field(default_factory=dict)
    vllm_client: Optional[Any] = None
    vllm_server_manager: Optional[Any] = None  # VLLMServerManager 实例


# 全局单例
_global_provider: Optional[Provider] = None
_provider_lock = threading.Lock()


def global_provider() -> Provider:
    """获取全局 Provider 单例。"""
    global _global_provider
    if _global_provider is None:
        with _provider_lock:
            if _global_provider is None:
                _global_provider = Provider()
    return _global_provider
