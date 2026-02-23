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
        try:
            import redis.asyncio as aioredis
        except ImportError:
            logger.warning("redis[asyncio] not installed, skipping Redis plugin")
            return

        # 从 dict 配置中解析 Redis 连接参数
        addresses = config.get("addresses", [])
        if addresses:
            address = addresses[0]
            if ":" in address:
                host, port_str = address.rsplit(":", 1)
                port = int(port_str)
            else:
                host = address
                port = 6379
        else:
            host = "localhost"
            port = 6379

        password = config.get("password", "") or None
        db = config.get("db", 0)
        max_connections = config.get("max_connections", 100)
        dial_timeout = config.get("dial_timeout", "5s")
        # 是否启用 SSL（需在配置中显式指定 ssl: true）
        ssl_enabled = config.get("ssl", False)

        # 解析超时（支持 "5s" 格式）
        timeout_seconds = None
        if isinstance(dial_timeout, str) and dial_timeout.endswith("s"):
            try:
                timeout_seconds = float(dial_timeout[:-1])
            except ValueError:
                pass
        elif isinstance(dial_timeout, (int, float)):
            timeout_seconds = float(dial_timeout)

        # 创建 Redis 客户端
        connect_kwargs = dict(
            host=host,
            port=port,
            password=password,
            db=db,
            max_connections=max_connections,
            socket_connect_timeout=timeout_seconds,
        )
        if ssl_enabled:
            connect_kwargs["ssl"] = True
            connect_kwargs["ssl_cert_reqs"] = None  # 不验证服务端证书

        client = aioredis.Redis(**connect_kwargs)

        # 测试连接
        await client.ping()

        # 注册到 provider
        from pkg.tide_date.provider import global_provider

        provider = global_provider()
        provider.redis = client

        logger.info(f"Redis installed: {host}:{port}/{db}")

    except ImportError:
        logger.warning("Redis dependencies not installed, skipping")
    except Exception as e:
        logger.warning(f"Failed to install Redis: {e}, skipping Redis plugin")
