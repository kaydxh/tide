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
        from tide.plugins.mysql import MySQLPlugin

        plugin = MySQLPlugin()
        await plugin.install(config)

        # Register to provider
        from pkg.tide_date.provider import global_provider

        provider = global_provider()
        provider.mysql = plugin.get_connection()

        logger.info(f"MySQL installed: {config.get('address', 'unknown')}")

    except ImportError:
        logger.warning("MySQL dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install MySQL: {e}")
        raise
