#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: MySQL - tide-date 的 MySQL 安装入口

通用逻辑已下沉到 peek.plugins.mysql，
本模块仅提供 register_callback 回调完成 provider 注册。
"""

import logging
from typing import Any, Dict

from peek.plugins.mysql import install_mysql as _install_mysql

logger = logging.getLogger(__name__)


async def _register_mysql_engine(engine):
    """将 MySQL engine 注册到 provider。"""
    from tide.provider import get_provider

    provider = get_provider()
    provider.set_mysql(engine)


async def install_mysql(config: Dict[str, Any], web_server=None):
    """安装 MySQL 连接。

    Args:
        config: MySQL 配置字典
        web_server: GenericWebServer 实例
    """
    await _install_mysql(config, web_server, register_callback=_register_mysql_engine)