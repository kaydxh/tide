#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置定义

参考 Go 版本 sea 的 configuration.proto 和 webserver.proto 实现
"""

import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


def parse_duration(value: Union[str, int, float, None]) -> float:
    """
    解析时间字符串

    支持格式：
    - 纯数字：直接作为秒
    - "10s": 10 秒
    - "5m": 5 分钟
    - "1h": 1 小时
    - "1h30m": 1 小时 30 分钟
    - "100ms": 100 毫秒

    Args:
        value: 时间值

    Returns:
        秒数（float）
    """
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return 0.0

    value = value.strip()
    if not value:
        return 0.0

    # 纯数字
    try:
        return float(value)
    except ValueError:
        pass

    # 解析带单位的时间
    total_seconds = 0.0
    pattern = r"(\d+(?:\.\d+)?)\s*(h|m|s|ms|us|ns)?"

    for match in re.finditer(pattern, value, re.IGNORECASE):
        num = float(match.group(1))
        unit = (match.group(2) or "s").lower()

        if unit == "h":
            total_seconds += num * 3600
        elif unit == "m":
            total_seconds += num * 60
        elif unit == "s":
            total_seconds += num
        elif unit == "ms":
            total_seconds += num / 1000
        elif unit == "us":
            total_seconds += num / 1000000
        elif unit == "ns":
            total_seconds += num / 1000000000

    return total_seconds


class NetConfig(BaseModel):
    """网络绑定配置"""

    host: str = Field(default="0.0.0.0", description="绑定地址")
    port: int = Field(default=8080, ge=1, le=65535, description="绑定端口")


class GrpcConfig(BaseModel):
    """gRPC 配置"""

    enabled: bool = Field(default=True, description="是否启用")
    port: int = Field(default=50051, ge=1, le=65535, description="gRPC 端口")
    timeout: float = Field(default=0, ge=0, description="超时时间（秒）")
    max_recv_msg_size: int = Field(
        default=4 * 1024 * 1024, ge=0, description="最大接收消息大小"
    )
    max_send_msg_size: int = Field(
        default=4 * 1024 * 1024, ge=0, description="最大发送消息大小"
    )

    @field_validator("timeout", mode="before")
    @classmethod
    def parse_timeout(cls, v):
        return parse_duration(v)


class HttpConfig(BaseModel):
    """HTTP 配置"""

    enabled: bool = Field(default=True, description="是否启用")
    read_timeout: float = Field(default=0, ge=0, description="读取超时时间（秒）")
    write_timeout: float = Field(default=0, ge=0, description="写入超时时间（秒）")
    max_request_body_size: int = Field(
        default=4 * 1024 * 1024, ge=0, description="最大请求体大小"
    )
    api_formatter: str = Field(default="trivial_api_v20", description="API 格式化器")

    @field_validator("read_timeout", "write_timeout", mode="before")
    @classmethod
    def parse_timeout(cls, v):
        return parse_duration(v)


class MethodQPSConfig(BaseModel):
    """方法级 QPS 配置"""

    method: str = Field(default="*", description="HTTP 方法或 gRPC 方法")
    path: str = Field(default="/", description="路径，支持前缀匹配")
    qps: float = Field(default=0, ge=0, description="QPS 限制")
    burst: int = Field(default=0, ge=0, description="突发容量")
    max_concurrency: int = Field(default=0, ge=0, description="最大并发数")


class QPSLimitConfig(BaseModel):
    """QPS 限流配置"""

    default_qps: float = Field(default=0, ge=0, description="默认 QPS")
    default_burst: int = Field(default=0, ge=0, description="默认突发容量")
    max_concurrency: int = Field(default=0, ge=0, description="最大并发数")
    wait_timeout: float = Field(default=0, ge=0, description="等待超时时间（秒）")
    method_qps: List[MethodQPSConfig] = Field(
        default_factory=list, description="方法级配置"
    )

    @field_validator("wait_timeout", mode="before")
    @classmethod
    def parse_wait_timeout(cls, v):
        return parse_duration(v)


class DebugConfig(BaseModel):
    """调试配置"""

    enabled: bool = Field(default=False, description="是否启用调试")
    enable_profiling: bool = Field(default=False, description="是否启用性能分析")
    profiling_path: str = Field(default="/debug/pprof", description="性能分析路径")


class ShutdownConfig(BaseModel):
    """关闭配置"""

    delay_duration: float = Field(default=0, ge=0, description="关闭延迟时间（秒）")
    timeout_duration: float = Field(default=5.0, ge=0, description="关闭超时时间（秒）")

    @field_validator("delay_duration", "timeout_duration", mode="before")
    @classmethod
    def parse_duration(cls, v):
        return parse_duration(v)


class WebConfig(BaseModel):
    """Web 服务器配置"""

    bind_address: NetConfig = Field(default_factory=NetConfig, description="绑定地址")
    grpc: GrpcConfig = Field(default_factory=GrpcConfig, description="gRPC 配置")
    http: HttpConfig = Field(default_factory=HttpConfig, description="HTTP 配置")
    debug: DebugConfig = Field(default_factory=DebugConfig, description="调试配置")
    shutdown: ShutdownConfig = Field(
        default_factory=ShutdownConfig, description="关闭配置"
    )
    http_qps_limit: Optional[QPSLimitConfig] = Field(
        default=None, description="HTTP QPS 限流配置"
    )
    grpc_qps_limit: Optional[QPSLimitConfig] = Field(
        default=None, description="gRPC QPS 限流配置"
    )


class LogConfig(BaseModel):
    """日志配置"""

    level: str = Field(default="info", description="日志级别")
    format: str = Field(default="text", description="日志格式 (text/json)")
    filepath: str = Field(default="./log", description="日志文件路径")
    max_age: float = Field(default=604800, ge=0, description="最大保留时间（秒）")
    rotate_interval: float = Field(default=3600, ge=0, description="轮转间隔（秒）")
    rotate_size: int = Field(default=100 * 1024 * 1024, ge=0, description="轮转大小")
    report_caller: bool = Field(default=False, description="是否报告调用者")

    @field_validator("max_age", "rotate_interval", mode="before")
    @classmethod
    def parse_duration(cls, v):
        return parse_duration(v)


class MySQLConfig(BaseModel):
    """MySQL 配置"""

    enabled: bool = Field(default=False, description="是否启用")
    host: str = Field(default="localhost", description="主机")
    port: int = Field(default=3306, ge=1, le=65535, description="端口")
    username: str = Field(default="root", description="用户名")
    password: str = Field(default="", description="密码")
    database: str = Field(default="", description="数据库名")
    charset: str = Field(default="utf8mb4", description="字符集")
    max_open_conns: int = Field(default=10, ge=0, description="最大连接数")
    max_idle_conns: int = Field(default=5, ge=0, description="最大空闲连接数")
    conn_max_lifetime: float = Field(default=3600, ge=0, description="连接最大生命周期（秒）")

    @property
    def dsn(self) -> str:
        """获取 DSN 连接字符串"""
        return (
            f"mysql+aiomysql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}?charset={self.charset}"
        )


class RedisConfig(BaseModel):
    """Redis 配置"""

    enabled: bool = Field(default=False, description="是否启用")
    addresses: List[str] = Field(
        default_factory=lambda: ["localhost:6379"], description="地址列表"
    )
    password: str = Field(default="", description="密码")
    database: int = Field(default=0, ge=0, le=15, description="数据库索引")
    pool_size: int = Field(default=10, ge=0, description="连接池大小")
    min_idle_conns: int = Field(default=5, ge=0, description="最小空闲连接数")
    dial_timeout: float = Field(default=5, ge=0, description="连接超时（秒）")
    read_timeout: float = Field(default=3, ge=0, description="读取超时（秒）")
    write_timeout: float = Field(default=3, ge=0, description="写入超时（秒）")


class DatabaseConfig(BaseModel):
    """数据库配置"""

    mysql: MySQLConfig = Field(default_factory=MySQLConfig, description="MySQL 配置")
    redis: RedisConfig = Field(default_factory=RedisConfig, description="Redis 配置")


class OpenTelemetryConfig(BaseModel):
    """OpenTelemetry 配置"""

    enabled: bool = Field(default=False, description="是否启用")
    service_name: str = Field(default="tide-service", description="服务名称")
    service_version: str = Field(default="1.0.0", description="服务版本")

    # Trace 配置
    trace_enabled: bool = Field(default=True, description="是否启用 Trace")
    trace_exporter_type: str = Field(
        default="otlp", description="Trace 导出器类型 (otlp/jaeger/stdout)"
    )
    trace_endpoint: str = Field(
        default="http://localhost:4317", description="Trace 导出端点"
    )
    trace_sample_ratio: float = Field(
        default=1.0, ge=0, le=1, description="Trace 采样率"
    )

    # Metric 配置
    metric_enabled: bool = Field(default=True, description="是否启用 Metric")
    metric_exporter_type: str = Field(
        default="otlp", description="Metric 导出器类型 (otlp/prometheus/stdout)"
    )
    metric_endpoint: str = Field(
        default="http://localhost:4317", description="Metric 导出端点"
    )
    metric_collect_duration: float = Field(
        default=60, ge=0, description="Metric 收集间隔（秒）"
    )

    @field_validator("metric_collect_duration", mode="before")
    @classmethod
    def parse_duration(cls, v):
        return parse_duration(v)


class TideConfig(BaseModel):
    """
    Tide 主配置

    对应 Go 版本 sea 的 Configuration
    """

    # 应用信息
    name: str = Field(default="tide-service", description="服务名称")
    version: str = Field(default="1.0.0", description="服务版本")

    # Web 服务器
    web: WebConfig = Field(default_factory=WebConfig, description="Web 服务器配置")

    # 日志
    log: LogConfig = Field(default_factory=LogConfig, description="日志配置")

    # 数据库
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig, description="数据库配置"
    )

    # 可观测性
    open_telemetry: OpenTelemetryConfig = Field(
        default_factory=OpenTelemetryConfig, description="OpenTelemetry 配置"
    )

    # 额外配置（用于扩展）
    extra: Dict[str, Any] = Field(default_factory=dict, description="额外配置")

    @model_validator(mode="after")
    def set_defaults(self):
        """设置默认值"""
        # 同步 OpenTelemetry 服务名
        if self.open_telemetry.service_name == "tide-service":
            self.open_telemetry.service_name = self.name
        if self.open_telemetry.service_version == "1.0.0":
            self.open_telemetry.service_version = self.version
        return self
