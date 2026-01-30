#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Repository - 仓储接口

参考 Go 版本 sea 的 domain/date/date.entity.repository.go 实现
定义领域层的仓储接口，由基础设施层实现
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from tide.ddd.entity import Entity

ID = TypeVar("ID")
E = TypeVar("E", bound=Entity)


class Repository(ABC, Generic[E, ID]):
    """
    同步仓储接口

    定义领域层需要的持久化操作，由基础设施层实现

    使用示例：
        class UserRepository(Repository[User, int]):
            def get_by_id(self, id: int) -> Optional[User]:
                # 实现
                pass
    """

    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[E]:
        """
        根据 ID 获取实体

        Args:
            id: 实体 ID

        Returns:
            实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_all(self) -> List[E]:
        """
        获取所有实体

        Returns:
            实体列表
        """
        pass

    @abstractmethod
    def save(self, entity: E) -> E:
        """
        保存实体（创建或更新）

        Args:
            entity: 实体

        Returns:
            保存后的实体
        """
        pass

    @abstractmethod
    def delete(self, id: ID) -> bool:
        """
        删除实体

        Args:
            id: 实体 ID

        Returns:
            是否删除成功
        """
        pass

    def exists(self, id: ID) -> bool:
        """
        检查实体是否存在

        Args:
            id: 实体 ID

        Returns:
            是否存在
        """
        return self.get_by_id(id) is not None


class AsyncRepository(ABC, Generic[E, ID]):
    """
    异步仓储接口

    用于异步 I/O 场景
    """

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[E]:
        """根据 ID 获取实体"""
        pass

    @abstractmethod
    async def get_all(self) -> List[E]:
        """获取所有实体"""
        pass

    @abstractmethod
    async def save(self, entity: E) -> E:
        """保存实体"""
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """删除实体"""
        pass

    async def exists(self, id: ID) -> bool:
        """检查实体是否存在"""
        return await self.get_by_id(id) is not None


class InMemoryRepository(Repository[E, ID], Generic[E, ID]):
    """
    内存仓储实现

    用于测试或简单场景
    """

    def __init__(self):
        self._storage: dict = {}

    def get_by_id(self, id: ID) -> Optional[E]:
        return self._storage.get(id)

    def get_all(self) -> List[E]:
        return list(self._storage.values())

    def save(self, entity: E) -> E:
        self._storage[entity.id] = entity
        return entity

    def delete(self, id: ID) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    def clear(self) -> None:
        """清空所有数据"""
        self._storage.clear()
