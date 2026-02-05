#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Config - 配置插件
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def install_config(config: Dict[str, Any]):
    """将配置安装到全局 provider。"""
    from pkg.tide_vllm.provider import global_provider

    provider = global_provider()
    provider.config = config

    logger.info(f"配置已安装: {list(config.keys())}")
