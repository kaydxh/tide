#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tide 配置加载器

基于 peek.config.ConfigLoader 的 Tide 专用配置加载器，
提供 Tide 框架的默认配置（TideConfig、TIDE 环境变量前缀等）。
"""

import logging
from pathlib import Path
from typing import Any, Dict, Type, TypeVar, Union

from pydantic import BaseModel

# 复用 peek 基础库的 ConfigLoader
from peek.config.loader import ConfigLoader as BaseConfigLoader

from tide.config.config import TideConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ConfigLoader(BaseConfigLoader):
    """
    Tide 配置加载器

    继承 peek.config.ConfigLoader，设置 Tide 默认的环境变量前缀为 "TIDE"。
    """

    def __init__(self, env_prefix: str = "TIDE"):
        super().__init__(env_prefix=env_prefix)


def load_config_from_file(
    path: Union[str, Path],
    model_class: Type[T] = TideConfig,
    load_env: bool = True,
    env_prefix: str = "TIDE",
) -> T:
    """
    从文件加载配置

    Args:
        path: 配置文件路径
        model_class: 模型类，默认为 TideConfig
        load_env: 是否加载环境变量

    Returns:
        配置模型
    """
    loader = ConfigLoader(env_prefix=env_prefix)
    loader.load_file(path)

    if load_env:
        loader.load_env()

    return loader.to_model(model_class)


def load_config(
    data: Dict[str, Any],
    model_class: Type[T] = TideConfig,
) -> T:
    """
    从字典加载配置

    Args:
        data: 配置字典
        model_class: 模型类，默认为 TideConfig

    Returns:
        配置模型
    """
    return model_class.model_validate(data)