#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置定义

参考 Go 版本 sea 的 configuration.proto 和 webserver.proto 实现
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

# 通用配置类已下沉到 peek 基础库
from peek.config.schema import (
    NetConfig,
    GrpcConfig,
    HttpConfig,
    MethodQPSConfig,
    QPSLimitConfig,
    DebugConfig,
    ShutdownConfig,
    WebConfig,
    LogConfig,
    OpenTelemetryConfig,
)


# ===== Tide 专有的配置类 =====

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
        if self.open_telemetry.service_name == "app-service":
            self.open_telemetry.service_name = self.name
        if self.open_telemetry.service_version == "1.0.0":
            self.open_telemetry.service_version = self.version
        return self