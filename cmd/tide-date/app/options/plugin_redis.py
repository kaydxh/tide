#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Redis - tide-date 的 Redis 安装入口

通用逻辑已下沉到 peek.plugins.redis，
本模块仅提供 register_callback 回调完成 provider 注册。
"""

import logging
from typing import Any, Dict

from peek.plugins.redis import install_redis as _install_redis

logger = logging.getLogger(__name__)


async def _register_redis_client(client):
    """将 Redis client 注册到 provider。"""
    from tide.provider import get_provider

    provider = get_provider()
    provider.set_redis(client)


async def install_redis(config: Dict[str, Any], web_server=None):
    """安装 Redis 连接。

    Args:
        config: Redis 配置字典
        web_server: GenericWebServer 实例
    """
    await _install_redis(config, web_server, register_callback=_register_redis_client)