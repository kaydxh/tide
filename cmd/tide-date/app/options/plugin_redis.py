#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Redis - Similar to sea's plugin.redis.go
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_redis(config: Dict[str, Any]):
    """Install Redis connection.

    Similar to sea's installRedisOrDie.
    """
    if not config or not config.get("enabled", False):
        logger.debug("Redis is disabled, skipping installation")
        return

    try:
        from tide.plugins.redis import RedisPlugin

        plugin = RedisPlugin()
        await plugin.install(config)

        # Register to provider
        from pkg.tide_date.provider import global_provider

        provider = global_provider()
        provider.redis = plugin.get_connection()

        logger.info(f"Redis installed: {config.get('addresses', ['unknown'])}")

    except ImportError:
        logger.warning("Redis dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install Redis: {e}")
        raise
