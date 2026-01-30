#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tide App 模块

提供应用程序核心组件：
- TideApp: 应用程序主类
- Command: 命令行支持
- Plugin: 插件机制
"""

from tide.app.application import TideApp
from tide.app.command import Command, CommandContext
from tide.app.plugin import Plugin, PluginManager
from tide.app.hooks import (
    HookType,
    HookEntry,
    HookManager,
    PostStartHook,
    PreShutdownHook,
)

__all__ = [
    "TideApp",
    "Command",
    "CommandContext",
    "Plugin",
    "PluginManager",
    "HookType",
    "HookEntry",
    "HookManager",
    "PostStartHook",
    "PreShutdownHook",
]
