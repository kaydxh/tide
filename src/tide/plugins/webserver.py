#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web 服务器插件

基于 peek 的 webserver 模块实现
"""

import logging
from typing import TYPE_CHECKING, Optional

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext
    from peek.net.webserver import GenericWebServer

logger = logging.getLogger(__name__)


class WebServerPlugin(Plugin):
    """
    Web 服务器插件

    初始化 HTTP/gRPC 服务器
    """

    name = "webserver"
    priority = 50  # 中等优先级

    def __init__(self):
        self._server: Optional["GenericWebServer"] = None

    async def install(self, ctx: "CommandContext") -> None:
        """安装 Web 服务器插件"""
        try:
            from peek.net.webserver import GenericWebServer, WebConfig as PeekWebConfig
        except ImportError:
            logger.error("peek.net.webserver not available")
            raise

        config = ctx.config
        web_config = config.web

        # 转换配置
        peek_config = PeekWebConfig(
            bind_address={
                "host": web_config.bind_address.host,
                "port": web_config.bind_address.port,
            },
            grpc={
                "enabled": web_config.grpc.enabled,
                "timeout": web_config.grpc.timeout,
            },
            http={
                "enabled": web_config.http.enabled,
                "read_timeout": web_config.http.read_timeout,
                "write_timeout": web_config.http.write_timeout,
            },
            debug={
                "enabled": web_config.debug.enabled,
                "enable_profiling": web_config.debug.enable_profiling,
            },
            shutdown={
                "delay_duration": web_config.shutdown.delay_duration,
                "timeout_duration": web_config.shutdown.timeout_duration,
            },
        )

        # 创建服务器
        self._server = GenericWebServer(peek_config)

        # 注册到 Provider
        ctx.provider.register("webserver", self._server)

        logger.info(
            f"WebServer plugin installed: "
            f"http://{web_config.bind_address.host}:{web_config.bind_address.port}"
        )

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 Web 服务器插件"""
        if self._server:
            # GenericWebServer 会在 run 结束后自动清理
            self._server = None
            logger.info("WebServer plugin uninstalled")

    @property
    def server(self) -> Optional["GenericWebServer"]:
        """获取服务器实例"""
        return self._server


async def create_web_server(web_config):
    """Create and configure web server.

    Factory function for creating GenericWebServer.

    Args:
        web_config: WebConfig dataclass with server configuration

    Returns:
        GenericWebServer instance
    """
    try:
        from peek.net.webserver import GenericWebServer
    except ImportError:
        logger.error("peek.net.webserver not available, using fallback FastAPI server")
        return await _create_fallback_server(web_config)

    # 获取配置值，处理 dict 和 dataclass 两种情况
    bind_address = getattr(web_config, 'bind_address', {}) or {}
    if isinstance(bind_address, dict):
        host = bind_address.get('host', '0.0.0.0')
        port = bind_address.get('port', 10001)
    else:
        host = getattr(bind_address, 'host', '0.0.0.0')
        port = getattr(bind_address, 'port', 10001)

    grpc_config = getattr(web_config, 'grpc', {}) or {}
    shutdown_config = getattr(web_config, 'shutdown', {}) or {}

    # 获取 gRPC 端口
    if isinstance(grpc_config, dict):
        grpc_enabled = grpc_config.get('enabled', False)
        grpc_port = grpc_config.get('port', None) if grpc_enabled else None
    else:
        grpc_enabled = getattr(grpc_config, 'enabled', False)
        grpc_port = getattr(grpc_config, 'port', None) if grpc_enabled else None

    # 获取 shutdown 配置
    if isinstance(shutdown_config, dict):
        shutdown_delay = shutdown_config.get('delay_duration', 0)
        shutdown_timeout = shutdown_config.get('timeout_duration', 5.0)
    else:
        shutdown_delay = getattr(shutdown_config, 'delay_duration', 0)
        shutdown_timeout = getattr(shutdown_config, 'timeout_duration', 5.0)

    # 创建服务器 - 使用构造函数参数
    server = GenericWebServer(
        host=host,
        port=port,
        grpc_port=grpc_port,
        shutdown_delay_duration=shutdown_delay,
        shutdown_timeout_duration=shutdown_timeout,
        title="Tide Date Service",
        description="Tide Date Service API",
        version="1.0.0",
    )

    logger.info(f"WebServer created: http://{host}:{port}")
    return server


async def _create_fallback_server(web_config):
    """Create fallback FastAPI server when peek is not available."""
    from fastapi import FastAPI, APIRouter
    import uvicorn

    # 获取配置值
    bind_address = getattr(web_config, 'bind_address', {}) or {}
    if isinstance(bind_address, dict):
        host = bind_address.get('host', '0.0.0.0')
        port = bind_address.get('port', 10001)
    else:
        host = getattr(bind_address, 'host', '0.0.0.0')
        port = getattr(bind_address, 'port', 10001)

    class FallbackWebServer:
        """Fallback web server using FastAPI directly."""

        def __init__(self):
            self.app = FastAPI(title="Tide Date Service")
            self.router = APIRouter()
            self.host = host
            self.port = port

        def get_router(self):
            """Get the API router."""
            return self.router

        async def run(self):
            """Run the server."""
            self.app.include_router(self.router)
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()

    server = FallbackWebServer()
    logger.info(f"Fallback WebServer created: http://{host}:{port}")
    return server
