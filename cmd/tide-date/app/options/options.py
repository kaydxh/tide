#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");

Server Run Options - tide-date 服务配置选项
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from peek.plugins.base_options import (
    BaseCompletedOptions,
    BaseServerRunOptions,
    LogConfig,
    WebConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置。"""

    mysql: Dict[str, Any] = field(default_factory=dict)
    redis: Dict[str, Any] = field(default_factory=dict)


class ServerRunOptions(BaseServerRunOptions):
    """tide-date 服务器运行选项。"""

    default_port = 10001

    def __init__(self, config_file: str):
        self.database_config: Optional[DatabaseConfig] = None
        super().__init__(config_file)

    def _load_business_config(self):
        """加载数据库业务配置。"""
        self.database_config = self._parse_database_config(
            self.config.get("database", {})
        )

    def _init_default_business_config(self):
        """初始化数据库默认配置。"""
        self.database_config = DatabaseConfig()

    def _parse_database_config(self, data: Dict[str, Any]) -> DatabaseConfig:
        """解析数据库配置。"""
        return DatabaseConfig(
            mysql=data.get("mysql", {}),
            redis=data.get("redis", {}),
        )

    def complete(self) -> "CompletedServerRunOptions":
        """完成设置默认 ServerRunOptions。"""
        return CompletedServerRunOptions(self)


class CompletedServerRunOptions(BaseCompletedOptions):
    """tide-date 服务已完成的服务器运行选项。"""

    _service_name = "tide-date"

    def _install_config(self):
        """将配置安装到 provider。"""
        from pkg.tide_date.provider import global_provider

        provider = global_provider()
        provider.config = self._options.config
        logger.info(f"配置已安装: {list(self._options.config.keys())}")

    async def _install_business(self, web_server):
        """安装 MySQL 和 Redis。"""
        from .plugin_mysql import install_mysql
        from .plugin_redis import install_redis

        await install_mysql(self._options.database_config.mysql, web_server)
        await install_redis(self._options.database_config.redis, web_server)

    def _install_web_handler(self, web_server):
        """安装 Web 处理器。"""
        from .plugin_web_handler import install_web_handler

        install_web_handler(web_server)