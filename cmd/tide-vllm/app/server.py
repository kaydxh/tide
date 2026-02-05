#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Tide VLLM Server - vLLM 模板示例服务
"""

import asyncio
from pathlib import Path
from typing import Optional

import click

from .options import ServerRunOptions


def new_command():
    """创建一个新的 click 命令，带有默认参数。"""

    @click.command()
    @click.option(
        "--config", "-c",
        type=click.Path(exists=True),
        default="./conf/tide-vllm.yaml",
        help="配置文件路径"
    )
    @click.option(
        "--version", "-v",
        is_flag=True,
        help="显示版本并退出"
    )
    def command(config: str, version: bool):
        """Tide VLLM Service - vLLM 模板示例服务，使用千问3模型。"""
        if version:
            from tide import __version__
            click.echo(f"tide-vllm version {__version__}")
            return

        run_command(config)

    return command


def run_command(config_file: str):
    """使用给定的配置运行服务器。"""
    options = ServerRunOptions(config_file)

    # 完成配置选项（设置默认值）
    completed_options = options.complete()

    # 运行服务器
    asyncio.run(completed_options.run())
