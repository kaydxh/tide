#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Redis - Similar to sea's plugin.redis.go

调用 peek.database.redis 的工厂函数创建连接，注册到 Provider。
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_redis(config: Dict[str, Any], web_server=None):
    """Install Redis connection.

    Similar to sea's installRedisOrDie.
    调用 peek.database.redis.create_redis_client 创建连接。

    Args:
        config: Redis 配置字典
        web_server: GenericWebServer 实例，用于注册 shutdown hook 以优雅关闭连接
    """
    if not config or not config.get("enabled", False):
        logger.debug("Redis is disabled, skipping installation")
        return

    try:
        from peek.database.redis import create_redis_client, close_redis_client

        client = await create_redis_client(config)

        if client is not None:
            # 注册到 provider
            from pkg.tide_date.provider import global_provider

            provider = global_provider()
            provider.redis = client

            # 注册 shutdown hook，在服务退出前主动关闭 Redis 连接
            if web_server is not None:
                web_server.add_pre_shutdown_hook(
                    "redis-close",
                    lambda: close_redis_client(client),
                )
                logger.info("Registered Redis shutdown hook")

    except ImportError:
        logger.warning("Redis dependencies not installed, skipping")
    except Exception as e:
        logger.warning(f"Failed to install Redis: {e}, skipping Redis plugin")