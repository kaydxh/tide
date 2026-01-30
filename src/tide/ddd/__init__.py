#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DDD 分层架构模块

提供领域驱动设计的基础组件：
- Entity: 实体基类
- ValueObject: 值对象基类
- Repository: 仓储接口
- Factory: 工厂模式
- Application: 应用层基类
"""

from tide.ddd.entity import Entity, AggregateRoot
from tide.ddd.value_object import ValueObject
from tide.ddd.repository import Repository, AsyncRepository
from tide.ddd.factory import Factory, FactoryConfig
from tide.ddd.application import Application, Command, Query, CommandHandler, QueryHandler
from tide.ddd.error import DomainError, EntityNotFoundError, ValidationError

__all__ = [
    # Entity
    "Entity",
    "AggregateRoot",
    # Value Object
    "ValueObject",
    # Repository
    "Repository",
    "AsyncRepository",
    # Factory
    "Factory",
    "FactoryConfig",
    # Application
    "Application",
    "Command",
    "Query",
    "CommandHandler",
    "QueryHandler",
    # Error
    "DomainError",
    "EntityNotFoundError",
    "ValidationError",
]
