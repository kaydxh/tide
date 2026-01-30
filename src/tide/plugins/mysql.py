#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL 插件

参考 Go 版本 sea 的 plugin.mysql.go 实现
"""

import logging
from typing import TYPE_CHECKING, Optional

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class MySQLPlugin(Plugin):
    """
    MySQL 插件

    初始化 MySQL 连接池
    """

    name = "mysql"
    priority = 80

    def __init__(self):
        self._engine = None

    def should_install(self, ctx: "CommandContext") -> bool:
        """检查是否应该安装"""
        if not ctx.config:
            return False
        return ctx.config.database.mysql.enabled

    async def install(self, ctx: "CommandContext") -> None:
        """安装 MySQL 插件"""
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
        except ImportError:
            logger.warning("SQLAlchemy not installed, skipping MySQL plugin")
            return

        config = ctx.config.database.mysql

        # 创建异步引擎
        self._engine = create_async_engine(
            config.dsn,
            pool_size=config.max_idle_conns,
            max_overflow=config.max_open_conns - config.max_idle_conns,
            pool_recycle=int(config.conn_max_lifetime),
            echo=False,
        )

        # 注册到 Provider
        ctx.provider.set_mysql(self._engine)
        logger.info(f"MySQL plugin installed: {config.host}:{config.port}/{config.database}")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 MySQL 插件"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            logger.info("MySQL plugin uninstalled")
