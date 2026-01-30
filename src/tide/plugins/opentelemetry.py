#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenTelemetry 插件

参考 Go 版本 sea 的 plugin.opentelemetry.go 实现
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

    初始化 Tracer 和 Meter
    """

    name = "opentelemetry"
    priority = 90  # 高优先级，在日志之后

    def __init__(self):
        self._tracer_provider = None
        self._meter_provider = None

    def should_install(self, ctx: "CommandContext") -> bool:
        """检查是否应该安装"""
        if not ctx.config:
            return False
        return ctx.config.open_telemetry.enabled

    async def install(self, ctx: "CommandContext") -> None:
        """安装 OpenTelemetry 插件"""
        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
        except ImportError:
            logger.warning("OpenTelemetry not installed, skipping plugin")
            return

        config = ctx.config.open_telemetry

        # 创建资源
        resource = Resource.create({
            SERVICE_NAME: config.service_name,
            SERVICE_VERSION: config.service_version,
        })

        # 配置 Tracer
        if config.trace_enabled:
            self._tracer_provider = TracerProvider(resource=resource)

            # 配置导出器
            try:
                if config.trace_exporter_type == "otlp":
                    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                    from opentelemetry.sdk.trace.export import BatchSpanProcessor

                    exporter = OTLPSpanExporter(endpoint=config.trace_endpoint)
                    self._tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

                elif config.trace_exporter_type == "stdout":
                    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

                    self._tracer_provider.add_span_processor(
                        SimpleSpanProcessor(ConsoleSpanExporter())
                    )
            except ImportError as e:
                logger.warning(f"Trace exporter not available: {e}")

            trace.set_tracer_provider(self._tracer_provider)
            tracer = trace.get_tracer(config.service_name)
            ctx.provider.set_tracer(tracer)
            logger.info(f"Tracer initialized: {config.trace_exporter_type}")

        # 配置 Meter
        if config.metric_enabled:
            self._meter_provider = MeterProvider(resource=resource)

            # 配置导出器
            try:
                if config.metric_exporter_type == "otlp":
                    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

                    exporter = OTLPMetricExporter(endpoint=config.metric_endpoint)
                    reader = PeriodicExportingMetricReader(
                        exporter,
                        export_interval_millis=int(config.metric_collect_duration * 1000),
                    )
                    self._meter_provider = MeterProvider(
                        resource=resource,
                        metric_readers=[reader],
                    )

                elif config.metric_exporter_type == "prometheus":
                    from opentelemetry.exporter.prometheus import PrometheusMetricReader

                    reader = PrometheusMetricReader()
                    self._meter_provider = MeterProvider(
                        resource=resource,
                        metric_readers=[reader],
                    )

                elif config.metric_exporter_type == "stdout":
                    from opentelemetry.sdk.metrics.export import (
                        ConsoleMetricExporter,
                        PeriodicExportingMetricReader,
                    )

                    reader = PeriodicExportingMetricReader(
                        ConsoleMetricExporter(),
                        export_interval_millis=int(config.metric_collect_duration * 1000),
                    )
                    self._meter_provider = MeterProvider(
                        resource=resource,
                        metric_readers=[reader],
                    )
            except ImportError as e:
                logger.warning(f"Metric exporter not available: {e}")

            metrics.set_meter_provider(self._meter_provider)
            meter = metrics.get_meter(config.service_name)
            ctx.provider.set_meter(meter)
            logger.info(f"Meter initialized: {config.metric_exporter_type}")

    async def uninstall(self, ctx: "CommandContext") -> None:
        """卸载 OpenTelemetry 插件"""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
            self._tracer_provider = None

        if self._meter_provider:
            self._meter_provider.shutdown()
            self._meter_provider = None

        logger.info("OpenTelemetry plugin uninstalled")
