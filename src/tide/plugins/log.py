#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志插件

桥接到 peek.logs 模块，利用 peek 完善的日志系统。
"""

import logging
from typing import TYPE_CHECKING

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class LogPlugin(Plugin):
    """
    日志插件

    桥接 tide 的 LogConfig 到 peek.logs.install_logs()
    """

    name = "log"
    priority = 100  # 最高优先级，首先安装

    async def install(self, ctx: "CommandContext") -> None:
        """安装日志插件"""
        config = ctx.config
        if not config:
            return

        log_config = config.log

        # 桥接到 peek.logs
        from peek.logs.config import LogConfig as PeekLogConfig, install_logs

        # 将 tide LogConfig 映射到 peek LogConfig
        # tide 的 format 字段映射到 peek 的 formatter 字段
        format_to_formatter = {
            "text": "text",
            "json": "json",
            "glog": "glog",
        }
        formatter = format_to_formatter.get(log_config.format.lower(), "glog")

        # 确定输出重定向
        redirect = "stdout"
        if log_config.filepath and log_config.filepath != "./log":
            redirect = "both"

        peek_log_config = PeekLogConfig(
            formatter=formatter,
            level=log_config.level,
            filepath=log_config.filepath,
            redirect=redirect,
            max_age=log_config.max_age,
            rotate_size=log_config.rotate_size,
            rotate_interval=log_config.rotate_interval,
            report_caller=log_config.report_caller,
        )

        install_logs(peek_log_config)
        logger.info(f"Log plugin installed (via peek.logs) with level={log_config.level}")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载日志插件"""
        logger.info("Log plugin uninstalled")