#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command - 命令和上下文

参考 Go 版本 sea 的 cobra.Command 实现
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from tide.app.application import TideApp
    from tide.config.config import TideConfig
    from tide.provider.provider import Provider


@dataclass
class Command:
    """
    命令定义

    Attributes:
        name: 命令名称
        func: 命令函数
        description: 命令描述
        aliases: 命令别名
    """

    name: str
    func: Callable
    description: str = ""
    aliases: list = field(default_factory=list)


@dataclass
class CommandContext:
    """
    命令执行上下文

    提供命令执行所需的所有依赖

    Attributes:
        app: 应用实例
        config: 配置
        provider: 依赖提供者
        extra: 额外数据
    """

    app: "TideApp"
    config: Optional["TideConfig"] = None
    provider: Optional["Provider"] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """获取额外数据"""
        return self.extra.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置额外数据"""
        self.extra[key] = value
