#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Server Run Options - Similar to sea's options.go
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from tide.config import ConfigLoader
from tide.plugins.monitor import MonitorConfig

logger = logging.getLogger(__name__)


@dataclass
class WebConfig:
    """Web server configuration."""

    bind_address: Dict[str, Any] = field(default_factory=lambda: {"port": 10001})
    grpc: Dict[str, Any] = field(default_factory=dict)
    http: Dict[str, Any] = field(default_factory=dict)
    debug: Dict[str, Any] = field(default_factory=dict)
    open_telemetry: Dict[str, Any] = field(default_factory=dict)
    qps_limit: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogConfig:
    """Log configuration."""

    formatter: str = "glog"
    level: str = "debug"
    filepath: str = "./log"
    max_age: str = "604800s"
    max_count: int = 200
    rotate_interval: str = "3600s"
    rotate_size: int = 104857600
    report_caller: bool = True
    redirect: str = "stdout"


@dataclass
class DatabaseConfig:
    """Database configuration."""

    mysql: Dict[str, Any] = field(default_factory=dict)
    redis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServerRunOptions:
    """Server run options.

    Similar to sea's ServerRunOptions struct.
    """

    config_file: str
    config: Dict[str, Any] = field(default_factory=dict)
    web_config: Optional[WebConfig] = None
    log_config: Optional[LogConfig] = None
    database_config: Optional[DatabaseConfig] = None
    monitor_config: Optional[MonitorConfig] = None

    def __post_init__(self):
        """Load configuration from file."""
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

            # Parse sub-configs
            self.web_config = self._parse_web_config(self.config.get("web", {}))
            self.log_config = self._parse_log_config(self.config.get("log", {}))
            self.database_config = self._parse_database_config(
                self.config.get("database", {})
            )
            self.monitor_config = self._parse_monitor_config(
                self.config.get("monitor", {})
            )
        else:
            logger.warning(f"Config file not found: {config_path}")
            self.web_config = WebConfig()
            self.log_config = LogConfig()
            self.database_config = DatabaseConfig()
            self.monitor_config = MonitorConfig()

    def _parse_web_config(self, data: Dict[str, Any]) -> WebConfig:
        """Parse web configuration."""
        return WebConfig(
            bind_address=data.get("bind_address", {"port": 10001}),
            grpc=data.get("grpc", {}),
            http=data.get("http", {}),
            debug=data.get("debug", {}),
            open_telemetry=data.get("open_telemetry", {}),
            qps_limit=data.get("qps_limit", {}),
        )

    def _parse_log_config(self, data: Dict[str, Any]) -> LogConfig:
        """Parse log configuration."""
        return LogConfig(
            formatter=data.get("formatter", "glog"),
            level=data.get("level", "debug"),
            filepath=data.get("filepath", "./log"),
            max_age=data.get("max_age", "604800s"),
            max_count=data.get("max_count", 200),
            rotate_interval=data.get("rotate_interval", "3600s"),
            rotate_size=data.get("rotate_size", 104857600),
            report_caller=data.get("report_caller", True),
            redirect=data.get("redirect", "stdout"),
        )

    def _parse_database_config(self, data: Dict[str, Any]) -> DatabaseConfig:
        """Parse database configuration."""
        return DatabaseConfig(
            mysql=data.get("mysql", {}),
            redis=data.get("redis", {}),
        )

    def _parse_monitor_config(self, data: Dict[str, Any]) -> MonitorConfig:
        """Parse monitor configuration."""
        return MonitorConfig.from_dict(data)

    def complete(self) -> "CompletedServerRunOptions":
        """Complete set default ServerRunOptions.

        Similar to sea's Complete() method.
        """
        return CompletedServerRunOptions(self)


class CompletedServerRunOptions:
    """Completed server run options.

    A wrapper that enforces a call of complete() before run can be invoked.
    Similar to sea's CompletedServerRunOptions.
    """

    def __init__(self, options: ServerRunOptions):
        self._options = options

    @property
    def options(self) -> ServerRunOptions:
        """Get the underlying options."""
        return self._options

    async def run(self):
        """Run the server.

        Similar to sea's Run method.
        """
        from tide import __version__

        logger.info(f"Starting tide-date version {__version__}")

        # Install plugins in order
        self._install_logs()
        self._install_config()

        # Create web server
        web_server = await self._create_web_server()

        # Install optional components based on config
        await self._install_mysql()
        await self._install_redis()
        await self._install_opentelemetry(web_server)

        # Install web handlers
        self._install_web_handler(web_server)

        # 安装监控插件
        await self._install_monitor(web_server)

        # Run the server
        # GenericWebServer.run() 是同步方法，使用 run_async() 进行异步运行
        if hasattr(web_server, 'run_async'):
            await web_server.run_async()
        else:
            # Fallback server
            await web_server.run()

    def _install_logs(self):
        """Install logging configuration."""
        from .plugin_logs import install_logs

        install_logs(self._options.log_config)

    def _install_config(self):
        """Install configuration to provider."""
        from .plugin_config import install_config

        install_config(self._options.config)

    async def _create_web_server(self):
        """Create and configure web server."""
        from tide.plugins.webserver import create_web_server

        return await create_web_server(self._options.web_config)

    async def _install_mysql(self):
        """Install MySQL if enabled."""
        from .plugin_mysql import install_mysql

        await install_mysql(self._options.database_config.mysql)

    async def _install_redis(self):
        """Install Redis if enabled."""
        from .plugin_redis import install_redis

        await install_redis(self._options.database_config.redis)

    async def _install_opentelemetry(self, web_server):
        """Install OpenTelemetry if enabled."""
        from .plugin_opentelemetry import install_opentelemetry

        await install_opentelemetry(
            self._options.web_config.open_telemetry,
            web_server
        )

    def _install_web_handler(self, web_server):
        """Install web handlers.

        Similar to sea's installWebHandlerOrDie.
        """
        from .plugin_web_handler import install_web_handler

        install_web_handler(web_server)

    async def _install_monitor(self, web_server):
        """安装监控插件。"""
        from tide.plugins.monitor import install_monitor

        await install_monitor(self._options.monitor_config, web_server)
