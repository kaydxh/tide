#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenTelemetry 插件

桥接到 peek.opentelemetry 模块，利用 peek 完善的 OpenTelemetry 系统。
"""

import logging
from typing import TYPE_CHECKING, Optional

from tide.app.plugin import Plugin

if TYPE_CHECKING:
    from tide.app.command import CommandContext

logger = logging.getLogger(__name__)


class OpenTelemetryPlugin(Plugin):
    """
    OpenTelemetry 插件

    桥接 tide 的 OpenTelemetryConfig 到 peek.opentelemetry.OpenTelemetryService
    """

    name = "opentelemetry"
    priority = 90  # 高优先级，在日志之后

    def __init__(self):
        self._service = None

    def should_install(self, ctx: "CommandContext") -> bool:
        """检查是否应该安装"""
        if not ctx.config:
            return False
        return ctx.config.open_telemetry.enabled

    async def install(self, ctx: "CommandContext") -> None:
        """安装 OpenTelemetry 插件"""
        try:
            from peek.opentelemetry import OpenTelemetryService, OpenTelemetryConfigBuilder
        except ImportError:
            logger.warning("peek.opentelemetry not available, skipping plugin")
            return

        config = ctx.config.open_telemetry

        # 使用 peek 的 ConfigBuilder 构建配置
        builder = OpenTelemetryConfigBuilder().with_enabled(True)

        # 配置 Resource
        builder = builder.with_resource(
            service_name=config.service_name,
            service_version=config.service_version,
        )

        # 配置 Tracer
        if config.trace_enabled:
            if config.trace_exporter_type == "otlp":
                builder = builder.with_tracer_otlp(
                    endpoint=config.trace_endpoint,
                    sample_ratio=config.trace_sample_ratio,
                )
            elif config.trace_exporter_type == "stdout":
                builder = builder.with_tracer_stdout()

        # 配置 Meter
        if config.metric_enabled:
            if config.metric_exporter_type == "otlp":
                builder = builder.with_metric_otlp(
                    endpoint=config.metric_endpoint,
                    collect_interval=f"{int(config.metric_collect_duration)}s",
                )
            elif config.metric_exporter_type == "prometheus":
                builder = builder.with_metric_prometheus()
            elif config.metric_exporter_type == "stdout":
                builder = builder.with_metric_stdout()

        # 构建并安装
        peek_config = builder.build()
        self._service = OpenTelemetryService(peek_config)
        self._service.install()

        # 将 tracer/meter 注册到 tide provider
        if self._service.tracer_provider and ctx.provider:
            try:
                from opentelemetry import trace
                tracer = trace.get_tracer(config.service_name)
                ctx.provider.set_tracer(tracer)
            except ImportError:
                pass

        if self._service.meter_provider and ctx.provider:
            try:
                from opentelemetry import metrics
                meter = metrics.get_meter(config.service_name)
                ctx.provider.set_meter(meter)
            except ImportError:
                pass

        logger.info("OpenTelemetry plugin installed (via peek.opentelemetry)")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 OpenTelemetry 插件"""
        if self._service:
            self._service.shutdown()
            self._service = None

        logger.info("OpenTelemetry plugin uninstalled")