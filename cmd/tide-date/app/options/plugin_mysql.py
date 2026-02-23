#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: MySQL - Similar to sea's plugin.mysql.go
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_mysql(config: Dict[str, Any]):
    """Install MySQL connection.

    Similar to sea's installMysqlOrDie.
    """
    if not config or not config.get("enabled", False):
        logger.debug("MySQL is disabled, skipping installation")
        return

    try:
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
        except ImportError:
            logger.warning("SQLAlchemy not installed, skipping MySQL plugin")
            return

        # 从 dict 配置中构建 MySQL DSN
        address = config.get("address", "localhost:3306")
        host_port = address.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        username = config.get("username", "root")
        password = config.get("password", "")
        db_name = config.get("db_name", "")
        max_connections = config.get("max_connections", 100)
        max_idle_connections = config.get("max_idle_connections", 10)

        dsn = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{db_name}"

        engine = create_async_engine(
            dsn,
            pool_size=max_idle_connections,
            max_overflow=max_connections - max_idle_connections,
            echo=False,
        )

        # Register to provider
        from pkg.tide_date.provider import global_provider

        provider = global_provider()
        provider.mysql = engine

        logger.info(f"MySQL installed: {address}/{db_name}")

    except ImportError:
        logger.warning("MySQL dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install MySQL: {e}")
        raise
