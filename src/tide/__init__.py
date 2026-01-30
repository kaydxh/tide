#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tide - Python Web/gRPC Service Framework

基于 Peek 基础库的服务框架，参考 Sea (Go版本) 的架构设计。

主要组件：
- TideApp: 应用程序主类
- Command: 命令行支持
- Plugin: 插件机制
- Config: 配置管理
- Provider: 依赖注入
"""

__version__ = "0.1.0"

from tide.app.application import TideApp
from tide.app.command import Command, CommandContext
from tide.app.plugin import Plugin, PluginManager
from tide.config.config import (
    TideConfig,
    WebConfig,
    LogConfig,
    DatabaseConfig,
    OpenTelemetryConfig,
)
from tide.config.loader import load_config, load_config_from_file
from tide.provider.provider import Provider, get_provider

__all__ = [
    # Version
    "__version__",
    # App
    "TideApp",
    "Command",
    "CommandContext",
    # Plugin
    "Plugin",
    "PluginManager",
    # Config
    "TideConfig",
    "WebConfig",
    "LogConfig",
    "DatabaseConfig",
    "OpenTelemetryConfig",
    "load_config",
    "load_config_from_file",
    # Provider
    "Provider",
    "get_provider",
]
