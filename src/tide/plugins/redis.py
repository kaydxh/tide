#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis 插件

参考 Go 版本 sea 的 plugin.redis.go 实现
"""

import logging
from typing import TYPE_CHECKING, Optional

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class RedisPlugin(Plugin):
    """
    Redis 插件

    初始化 Redis 连接
    """

    name = "redis"
    priority = 80

    def __init__(self):
        self._client = None

    def should_install(self, ctx: "CommandContext") -> bool:
        """检查是否应该安装"""
        if not ctx.config:
            return False
        return ctx.config.database.redis.enabled

    async def install(self, ctx: "CommandContext") -> None:
        """安装 Redis 插件"""
        try:
            import redis.asyncio as aioredis
        except ImportError:
            logger.warning("Redis not installed, skipping Redis plugin")
            return

        config = ctx.config.database.redis

        # 解析地址
        if config.addresses:
            address = config.addresses[0]
            if ":" in address:
                host, port = address.rsplit(":", 1)
                port = int(port)
            else:
                host = address
                port = 6379
        else:
            host = "localhost"
            port = 6379

        # 创建 Redis 客户端
        self._client = aioredis.Redis(
            host=host,
            port=port,
            password=config.password or None,
            db=config.database,
            max_connections=config.pool_size,
            socket_timeout=config.read_timeout,
            socket_connect_timeout=config.dial_timeout,
        )

        # 测试连接
        try:
            await self._client.ping()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        # 注册到 Provider
        ctx.provider.set_redis(self._client)
        logger.info(f"Redis plugin installed: {host}:{port}")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 Redis 插件"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis plugin uninstalled")
