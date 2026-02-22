#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor 插件 - 进程资源监控

基于 peek.os.monitor 模块实现，提供：
1. 进程 CPU、内存、GPU、显存监控
2. HTTP API 端点（/debug/monitor/*）
3. 支持按需快照和持续采集
4. 支持 HTML/JSON 报告生成

该插件可被 tide 下所有 cmd 应用复用。
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    """进程监控配置。

    Attributes:
        enabled: 是否启用监控插件。
        auto_start: 是否在启动时自动开始持续采集（false 则只提供按需快照 API）。
        interval: 采集间隔（秒），仅持续采集模式有效。
        enable_gpu: 是否启用 GPU 监控（需要 pynvml）。
        include_children: 是否监控子进程（如 vLLM server）。
        history_size: 历史记录最大条数。
    """

    enabled: bool = False
    auto_start: bool = False
    interval: float = 5.0
    enable_gpu: bool = True
    include_children: bool = True
    history_size: int = 3600

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonitorConfig":
        """从字典创建配置。

        Args:
            data: 配置字典（通常来自 YAML 解析）

        Returns:
            MonitorConfig 实例
        """
        return cls(
            enabled=data.get("enabled", False),
            auto_start=data.get("auto_start", False),
            interval=data.get("interval", 5.0),
            enable_gpu=data.get("enable_gpu", True),
            include_children=data.get("include_children", True),
            history_size=data.get("history_size", 3600),
        )


# 全局 MonitorService 实例
_monitor_service = None


def get_monitor_service():
    """获取全局 MonitorService 实例。

    Returns:
        MonitorService 实例，如果未初始化则返回 None
    """
    return _monitor_service


class MonitorPlugin(Plugin):
    """进程资源监控插件

    继承 Plugin 基类，提供标准的 install/uninstall 生命周期管理。

    使用方式（基于 PluginManager）：
        >>> plugin_manager.register(MonitorPlugin())
        >>> await plugin_manager.install_all(ctx)
    """

    name = "monitor"
    priority = 5  # 低优先级，在其他插件之后安装（确保子进程已启动）

    def __init__(self):
        self._service = None

    def should_install(self, ctx: "CommandContext") -> bool:
        """检查是否应该安装。"""
        if not ctx.config:
            return False
        monitor_config = getattr(ctx.config, "monitor", None)
        if monitor_config is None:
            return False
        if isinstance(monitor_config, dict):
            return monitor_config.get("enabled", False)
        return getattr(monitor_config, "enabled", False)

    async def install(self, ctx: "CommandContext") -> None:
        """安装监控插件。"""
        global _monitor_service

        monitor_config = getattr(ctx.config, "monitor", {})
        if isinstance(monitor_config, dict):
            config = MonitorConfig.from_dict(monitor_config)
        else:
            config = monitor_config

        web_server = ctx.provider.get("webserver") if ctx.provider else None
        self._service = await install_monitor(config, web_server)

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载监控插件。"""
        await uninstall_monitor()
        self._service = None

    @property
    def service(self):
        """获取 MonitorService 实例。"""
        return self._service


async def install_monitor(
    config: Optional[MonitorConfig], web_server=None
) -> Optional[Any]:
    """安装监控插件（函数式接口）。

    提供无需 PluginManager 的简便安装方式，适合在各 cmd 应用的
    CompletedServerRunOptions.run() 中直接调用。

    Args:
        config: 监控配置，为 None 或 enabled=False 时跳过安装
        web_server: Web 服务器实例（用于注册 API 路由），
                    需要有 app 属性（FastAPI 实例）

    Returns:
        MonitorService 实例，如果未启用则返回 None

    Example:
        >>> from tide.plugins.monitor import install_monitor, MonitorConfig
        >>> config = MonitorConfig(enabled=True, interval=5.0)
        >>> service = await install_monitor(config, web_server)
    """
    global _monitor_service

    if config is None or not config.enabled:
        logger.info("监控插件未启用")
        return None

    try:
        # 检查依赖
        try:
            import psutil  # noqa: F401
        except ImportError:
            logger.error(
                "psutil 未安装，监控插件需要 psutil。请运行: pip install psutil"
            )
            return None

        try:
            from peek.os.monitor.service import (
                MonitorService,
                MonitorServiceConfig,
                register_monitor_routes,
            )
        except ImportError:
            logger.error(
                "peek.os.monitor.service 模块未安装，监控插件需要 peek 库"
            )
            return None

        # 将 tide MonitorConfig 转换为 peek MonitorServiceConfig
        service_config = MonitorServiceConfig(
            enabled=config.enabled,
            auto_start=config.auto_start,
            interval=config.interval,
            enable_gpu=config.enable_gpu,
            include_children=config.include_children,
            history_size=config.history_size,
        )

        # 创建监控服务
        service = MonitorService(service_config)
        _monitor_service = service

        # 注册 API 路由
        if web_server is not None:
            # 获取 FastAPI app
            app = getattr(web_server, "app", None)
            if app is None:
                router = getattr(web_server, "router", None)
                if router is not None:
                    app = router
            if app is not None:
                register_monitor_routes(app, service)
            else:
                logger.warning(
                    "web_server 没有 app 或 router 属性，无法注册监控 API 路由"
                )

        # 如果配置了自动启动，则开始持续采集
        if config.auto_start:
            logger.info("monitor.auto_start=true，正在启动持续采集...")
            result = service.start_collecting()
            logger.info(f"持续采集启动结果: {result}")

        logger.info(
            f"监控插件已安装: interval={config.interval}s, "
            f"enable_gpu={config.enable_gpu}, "
            f"include_children={config.include_children}, "
            f"auto_start={config.auto_start}"
        )

        return service

    except Exception as e:
        logger.error(f"安装监控插件失败: {e}", exc_info=True)
        raise


async def uninstall_monitor() -> None:
    """卸载监控插件。"""
    global _monitor_service

    if _monitor_service is not None:
        _monitor_service.shutdown()
        _monitor_service = None
        logger.info("监控插件已卸载")
