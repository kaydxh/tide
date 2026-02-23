#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis 插件

基于 peek.database.redis 的 Tide 专用插件封装。
参考 Go 版本 sea 的 plugin.redis.go 实现。
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

    封装 peek.database.redis 的工厂函数，
    负责生命周期管理和 Provider 注册。
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
        """安装 Redis 插件，调用 peek.database.redis 工厂函数"""
        from peek.database.redis import create_redis_client

        config = ctx.config.database.redis
        self._client = await create_redis_client(config)

        if self._client is not None:
            # 注册到 Provider
            ctx.provider.set_redis(self._client)

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 Redis 插件"""
        from peek.database.redis import close_redis_client

        if self._client:
            await close_redis_client(self._client)
            self._client = None