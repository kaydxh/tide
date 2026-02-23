# -*- coding: utf-8 -*-
"""Chat Factory - 从 peek 重导出

核心实现已下沉到 peek.ai.vllm.chat.factory。
"""

from peek.ai.vllm.chat.factory import ChatFactory, FactoryConfig

__all__ = ["ChatFactory", "FactoryConfig"]