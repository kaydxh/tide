#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web 服务器插件

基于 peek 的 webserver 模块实现。
工厂函数已下沉到 peek.net.webserver.factory。
"""

import logging
from typing import TYPE_CHECKING, Optional

from tide.app.plugin import Plugin

# 从 peek 基础库导入工厂函数
from peek.net.webserver.factory import create_web_server

if TYPE_CHECKING:
    from tide.app.command import CommandContext
    from peek.net.webserver import GenericWebServer

logger = logging.getLogger(__name__)


class WebServerPlugin(Plugin):
    """
    Web 服务器插件

    初始化 HTTP/gRPC 服务器，复用 peek 的 create_web_server 工厂函数。
    """

    name = "webserver"
    priority = 50  # 中等优先级

    def __init__(self):
        self._server: Optional["GenericWebServer"] = None

    async def install(self, ctx: "CommandContext") -> None:
        """安装 Web 服务器插件"""
        config = ctx.config
        web_config = config.web

        # 复用 peek 的工厂函数创建服务器
        self._server = await create_web_server(
            web_config,
            title=config.name,
            description=f"{config.name} API",
            version=config.version,
        )

        # 注册到 Provider
        ctx.provider.register("webserver", self._server)

        host = web_config.bind_address.host
        port = web_config.bind_address.port
        logger.info(
            f"WebServer plugin installed: http://{host}:{port}"
        )

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 Web 服务器插件"""
        if self._server:
            self._server = None
            logger.info("WebServer plugin uninstalled")

    @property
    def server(self) -> Optional["GenericWebServer"]:
        """获取服务器实例"""
        return self._server