#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TideApp - 应用程序主类

基于 peek.app.application.BaseApp，添加 Tide 特有的配置加载。
"""

import logging
from typing import Optional

from peek.app.application import BaseApp

from tide.app.command import CommandContext
from tide.config.config import TideConfig
from tide.provider.provider import Provider, get_provider

logger = logging.getLogger(__name__)


class TideApp(BaseApp):
    """
    Tide 应用程序主类

    继承 peek.app.BaseApp，添加：
    - TideConfig 配置加载
    - Tide 专用 CommandContext

    使用示例：
        app = TideApp(name="my-service")

        @app.command()
        def serve(config: str = "conf/config.yaml"):
            app.run_with_config(config)

        if __name__ == "__main__":
            app.cli()
    """

    def __init__(
        self,
        name: str,
        version: str = "0.1.0",
        description: str = "",
    ):
        super().__init__(name=name, version=version, description=description)
        # 使用 Tide 专用的 Provider
        self._provider: Provider = get_provider()

    def run_with_config(self, config_path: str) -> None:
        """
        使用配置文件启动应用

        Args:
            config_path: 配置文件路径
        """
        from tide.config.loader import load_config_from_file

        config = load_config_from_file(config_path)
        self.run(config)

    def run(self, config: TideConfig) -> None:
        """
        启动应用

        Args:
            config: Tide 应用配置
        """
        super().run(config)

    def _create_command_context(self) -> CommandContext:
        """
        创建 Tide 专用命令上下文

        Returns:
            Tide CommandContext 实例
        """
        return CommandContext(
            app=self,
            config=self._config,
            provider=self._provider,
        )

    @property
    def config(self) -> Optional[TideConfig]:
        """获取配置"""
        return self._config

    @property
    def provider(self) -> Provider:
        """获取 Provider"""
        return self._provider