#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");

Server Run Options - vLLM 服务配置选项
"""

import logging
from typing import Any, Dict, Optional

from peek.plugins.base_options import (
    BaseCompletedOptions,
    BaseServerRunOptions,
    LogConfig,
    WebConfig,
)
from peek.plugins.vllm import VLLMConfig, parse_vllm_config

logger = logging.getLogger(__name__)


class ServerRunOptions(BaseServerRunOptions):
    """vLLM 服务器运行选项。"""

    default_port = 10002

    def __init__(self, config_file: str):
        self.vllm_config: Optional[VLLMConfig] = None
        super().__init__(config_file)

    def _load_business_config(self):
        """加载 vLLM 业务配置。"""
        self.vllm_config = parse_vllm_config(self.config.get("vllm", {}))

    def _init_default_business_config(self):
        """初始化 vLLM 默认配置。"""
        self.vllm_config = VLLMConfig()

    def complete(self) -> "CompletedServerRunOptions":
        """完成设置默认 ServerRunOptions。"""
        return CompletedServerRunOptions(self)


class CompletedServerRunOptions(BaseCompletedOptions):
    """vLLM 服务已完成的服务器运行选项。"""

    _service_name = "tide-vllm"

    def _install_config(self):
        """将配置安装到 provider。"""
        from tide.provider import get_provider

        provider = get_provider()
        provider.set_config(self._options.config)
        logger.info(f"配置已安装: {list(self._options.config.keys())}")

    async def _install_business(self, web_server):
        """安装 vLLM 客户端。"""
        from .plugin_vllm import install_vllm

        await install_vllm(self._options.vllm_config)

    def _install_web_handler(self, web_server):
        """安装 Web 处理器。"""
        from .plugin_web_handler import install_web_handler

        install_web_handler(web_server)