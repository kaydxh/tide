#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider - 全局依赖注入容器

基于 peek.app.provider 的 Tide 专用 Provider，
添加 MySQL/Redis/Tracer/Meter 等业务快捷方法。
"""

import logging
from typing import Any, Optional

# 从 peek 基础库导入通用 Provider
from peek.app.provider import Provider as BaseProvider

logger = logging.getLogger(__name__)


class Provider(BaseProvider):
    """
    Tide Provider

    继承 peek.app.Provider，添加 Tide 业务常用的快捷方法。
    """

    # 子类需要自己的单例变量，避免与基类共享
    _instance: Optional["Provider"] = None
    _lock = __import__("threading").Lock()

    # 常用依赖的快捷方法

    def set_mysql(self, client: Any) -> None:
        """设置 MySQL 客户端"""
        self.register("mysql", client, overwrite=True)

    def get_mysql(self) -> Optional[Any]:
        """获取 MySQL 客户端"""
        return self.get("mysql")

    def set_redis(self, client: Any) -> None:
        """设置 Redis 客户端"""
        self.register("redis", client, overwrite=True)

    def get_redis(self) -> Optional[Any]:
        """获取 Redis 客户端"""
        return self.get("redis")

    def set_tracer(self, tracer: Any) -> None:
        """设置 Tracer"""
        self.register("tracer", tracer, overwrite=True)

    def get_tracer(self) -> Optional[Any]:
        """获取 Tracer"""
        return self.get("tracer")

    def set_meter(self, meter: Any) -> None:
        """设置 Meter"""
        self.register("meter", meter, overwrite=True)

    def get_meter(self) -> Optional[Any]:
        """获取 Meter"""
        return self.get("meter")


# 全局单例获取函数
def get_provider() -> Provider:
    """
    获取全局 Provider 实例

    Returns:
        Tide Provider 单例
    """
    return Provider()