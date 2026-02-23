#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: MySQL - Similar to sea's plugin.mysql.go

调用 peek.database.mysql 的工厂函数创建连接，注册到 Provider。
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_mysql(config: Dict[str, Any], web_server=None):
    """Install MySQL connection.

    Similar to sea's installMysqlOrDie.
    调用 peek.database.mysql.create_mysql_engine 创建连接。

    Args:
        config: MySQL 配置字典
        web_server: GenericWebServer 实例，用于注册 shutdown hook 以优雅关闭连接池
    """
    if not config or not config.get("enabled", False):
        logger.debug("MySQL is disabled, skipping installation")
        return

    try:
        from peek.database.mysql import create_mysql_engine, close_mysql_engine

        engine = await create_mysql_engine(config)

        if engine is not None:
            # 注册到 provider
            from pkg.tide_date.provider import global_provider

            provider = global_provider()
            provider.mysql = engine

            # 注册 shutdown hook，在服务退出前主动关闭连接池
            # 避免事件循环关闭后 aiomysql Connection.__del__ 报 RuntimeError
            if web_server is not None:
                web_server.add_pre_shutdown_hook(
                    "mysql-close",
                    lambda: close_mysql_engine(engine),
                )
                logger.info("Registered MySQL shutdown hook")

    except ImportError:
        logger.warning("MySQL dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install MySQL: {e}")
        raise