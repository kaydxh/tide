#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin - 插件机制

基于 peek.app.plugin 的 Tide 专用插件，
保留对 CommandContext 的类型约束。
"""

import logging
from typing import TYPE_CHECKING

# 从 peek 基础库导入通用插件机制
from peek.app.plugin import Plugin as BasePlugin
from peek.app.plugin import PluginManager

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class Plugin(BasePlugin):
    """
    Tide 插件基类

    继承 peek.app.Plugin，添加 CommandContext 类型提示。
    """

    async def install(self, ctx: "CommandContext") -> None:
        """
        安装插件

        Args:
            ctx: 命令上下文
        """
        pass

    async def uninstall(self, ctx: "CommandContext") -> None:
        """
        卸载插件

        Args:
            ctx: 命令上下文
        """
        pass

    def should_install(self, ctx: "CommandContext") -> bool:
        """
        判断是否应该安装

        Args:
            ctx: 命令上下文

        Returns:
            是否应该安装
        """
        return self.enabled


__all__ = [
    "Plugin",
    "PluginManager",
]