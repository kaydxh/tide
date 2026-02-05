# -*- coding: utf-8 -*-
"""Application - 应用层定义

定义应用层的命令和处理器
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chat_handler import ChatHandler


@dataclass
class Commands:
    """命令集合"""
    chat_handler: "ChatHandler"


@dataclass
class Application:
    """应用层
    
    包含所有命令处理器
    """
    commands: Commands
