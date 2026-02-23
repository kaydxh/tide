#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command - 命令和上下文

基于 peek.app.command 的 Tide 专用命令上下文，
添加 TideApp/TideConfig/Provider 的类型约束。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

# 从 peek 基础库重导出
from peek.app.command import Command

if TYPE_CHECKING:
    from tide.app.application import TideApp
    from tide.config.config import TideConfig
    from tide.provider.provider import Provider


@dataclass
class CommandContext:
    """
    Tide 命令执行上下文

    继承 peek.app.command.CommandContext 的概念，
    添加 Tide 特定的类型约束。

    Attributes:
        app: TideApp 应用实例
        config: TideConfig 配置
        provider: Tide Provider
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


__all__ = [
    "Command",
    "CommandContext",
]
