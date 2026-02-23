#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: MySQL - Similar to sea's plugin.mysql.go

调用 peek.database.mysql 的工厂函数创建连接，注册到 Provider。
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_mysql(config: Dict[str, Any]):
    """Install MySQL connection.

    Similar to sea's installMysqlOrDie.
    调用 peek.database.mysql.create_mysql_engine 创建连接。
    """
    if not config or not config.get("enabled", False):
        logger.debug("MySQL is disabled, skipping installation")
        return

    try:
        from peek.database.mysql import create_mysql_engine

        engine = await create_mysql_engine(config)

        if engine is not None:
            # 注册到 provider
            from pkg.tide_date.provider import global_provider

            provider = global_provider()
            provider.mysql = engine

    except ImportError:
        logger.warning("MySQL dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install MySQL: {e}")
        raise