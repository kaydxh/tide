#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider 模块

提供全局依赖注入容器
"""

from tide.provider.provider import Provider, get_provider

__all__ = [
    "Provider",
    "get_provider",
]
