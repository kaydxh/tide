#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志插件

参考 Go 版本 sea 的 plugin.logs.go 实现
"""

import logging
import sys
from typing import TYPE_CHECKING

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class LogPlugin(Plugin):
    """
    日志插件

    配置日志系统
    """

    name = "log"
    priority = 100  # 最高优先级，首先安装

    async def install(self, ctx: "CommandContext") -> None:
        """安装日志插件"""
        config = ctx.config
        if not config:
            return

        log_config = config.log

        # 配置日志级别
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "warn": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        level = level_map.get(log_config.level.lower(), logging.INFO)

        # 配置日志格式
        if log_config.format.lower() == "json":
            # JSON 格式
            try:
                import json

                class JsonFormatter(logging.Formatter):
                    def format(self, record):
                        log_obj = {
                            "timestamp": self.formatTime(record),
                            "level": record.levelname,
                            "logger": record.name,
                            "message": record.getMessage(),
                        }
                        if record.exc_info:
                            log_obj["exception"] = self.formatException(record.exc_info)
                        if log_config.report_caller:
                            log_obj["file"] = record.filename
                            log_obj["line"] = record.lineno
                            log_obj["function"] = record.funcName
                        return json.dumps(log_obj, ensure_ascii=False)

                formatter = JsonFormatter()
            except Exception:
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
        else:
            # 文本格式
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            if log_config.report_caller:
                fmt = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            formatter = logging.Formatter(fmt)

        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # TODO: 添加文件处理器（如果配置了 filepath）

        logger.info(f"Log plugin installed with level={log_config.level}")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载日志插件"""
        logger.info("Log plugin uninstalled")
