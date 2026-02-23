#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL 插件

基于 peek.database.mysql 的 Tide 专用插件封装。
参考 Go 版本 sea 的 plugin.mysql.go 实现。
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

    封装 peek.database.mysql 的工厂函数，
    负责生命周期管理和 Provider 注册。
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
        """安装 MySQL 插件，调用 peek.database.mysql 工厂函数"""
        from peek.database.mysql import create_mysql_engine

        config = ctx.config.database.mysql
        self._engine = await create_mysql_engine(config)

        if self._engine is not None:
            # 注册到 Provider
            ctx.provider.set_mysql(self._engine)

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 MySQL 插件"""
        from peek.database.mysql import close_mysql_engine

        if self._engine:
            await close_mysql_engine(self._engine)
            self._engine = None