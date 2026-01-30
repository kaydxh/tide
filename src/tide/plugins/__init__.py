#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内置插件模块

提供常用的插件实现：
- LogPlugin: 日志插件
- MySQLPlugin: MySQL 插件
- RedisPlugin: Redis 插件
- OpenTelemetryPlugin: OpenTelemetry 插件
- WebServerPlugin: Web 服务器插件
"""

from tide.plugins.log import LogPlugin
from tide.plugins.mysql import MySQLPlugin
from tide.plugins.redis import RedisPlugin
from tide.plugins.opentelemetry import OpenTelemetryPlugin
from tide.plugins.webserver import WebServerPlugin

__all__ = [
    "LogPlugin",
    "MySQLPlugin",
    "RedisPlugin",
    "OpenTelemetryPlugin",
    "WebServerPlugin",
]
