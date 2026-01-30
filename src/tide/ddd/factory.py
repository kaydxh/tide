#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Factory - 工厂模式

参考 Go 版本 sea 的 domain/date/date.entity.factory.go 实现
用于创建复杂的领域对象
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from pydantic import BaseModel

from tide.ddd.entity import Entity
from tide.ddd.repository import Repository

E = TypeVar("E", bound=Entity)
ID = TypeVar("ID")


@dataclass
class FactoryConfig:
    """
    工厂配置

    存储工厂所需的依赖

    Attributes:
        repositories: 仓储字典
        services: 服务字典
        extra: 额外配置
    """

    repositories: Dict[str, Any] = field(default_factory=dict)
    services: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def get_repository(self, name: str) -> Optional[Any]:
        """获取仓储"""
        return self.repositories.get(name)

    def get_service(self, name: str) -> Optional[Any]:
        """获取服务"""
        return self.services.get(name)


class Factory(ABC, Generic[E]):
    """
    工厂基类

    用于创建复杂的领域对象，封装创建逻辑

    使用示例：
        class UserFactory(Factory[User]):
            def __init__(self, config: FactoryConfig):
                super().__init__(config)
                self.user_repo = config.get_repository("user")

            def create(self, **kwargs) -> User:
                user = User(**kwargs)
                # 额外的初始化逻辑
                return user

            def create_with_validation(self, **kwargs) -> User:
                # 验证逻辑
                return self.create(**kwargs)
    """

    def __init__(self, config: Optional[FactoryConfig] = None):
        """
        初始化工厂

        Args:
            config: 工厂配置
        """
        self._config = config or FactoryConfig()

    @property
    def config(self) -> FactoryConfig:
        """获取配置"""
        return self._config

    @abstractmethod
    def create(self, **kwargs: Any) -> E:
        """
        创建实体

        Args:
            **kwargs: 创建参数

        Returns:
            实体实例
        """
        pass


class SimpleFactory(Factory[E], Generic[E]):
    """
    简单工厂

    直接根据类型创建实体
    """

    def __init__(
        self,
        entity_class: Type[E],
        config: Optional[FactoryConfig] = None,
    ):
        """
        初始化简单工厂

        Args:
            entity_class: 实体类
            config: 工厂配置
        """
        super().__init__(config)
        self._entity_class = entity_class

    def create(self, **kwargs: Any) -> E:
        """创建实体"""
        return self._entity_class(**kwargs)


class BuilderFactory(Factory[E], Generic[E]):
    """
    构建器工厂

    支持链式构建实体
    """

    def __init__(
        self,
        entity_class: Type[E],
        config: Optional[FactoryConfig] = None,
    ):
        super().__init__(config)
        self._entity_class = entity_class
        self._attrs: Dict[str, Any] = {}

    def with_attr(self, key: str, value: Any) -> "BuilderFactory[E]":
        """设置属性"""
        self._attrs[key] = value
        return self

    def create(self, **kwargs: Any) -> E:
        """创建实体"""
        attrs = {**self._attrs, **kwargs}
        entity = self._entity_class(**attrs)
        self._attrs.clear()
        return entity

    def reset(self) -> "BuilderFactory[E]":
        """重置构建器"""
        self._attrs.clear()
        return self
