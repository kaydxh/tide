#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entity - 实体基类

参考 Go 版本 sea 的 domain/date/date.entity.go 实现
"""

from abc import ABC
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


ID = TypeVar("ID")


class Entity(BaseModel, ABC, Generic[ID]):
    """
    实体基类

    实体是具有唯一标识的领域对象

    Attributes:
        id: 唯一标识
        created_at: 创建时间
        updated_at: 更新时间
    """

    id: Optional[ID] = Field(default=None, description="唯一标识")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        """Pydantic 配置"""
        from_attributes = True

    def __eq__(self, other: Any) -> bool:
        """实体相等性比较（基于 ID）"""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """哈希值（基于 ID）"""
        return hash(self.id)

    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()


class AggregateRoot(Entity[ID], Generic[ID]):
    """
    聚合根基类

    聚合根是一组相关对象的入口点，负责维护聚合内的一致性

    Attributes:
        version: 版本号（用于乐观锁）
    """

    version: int = Field(default=0, description="版本号")

    def increment_version(self) -> None:
        """增加版本号"""
        self.version += 1
        self.update_timestamp()


class StringEntity(Entity[str]):
    """字符串 ID 实体"""

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一标识")


class UUIDEntity(Entity[UUID]):
    """UUID 实体"""

    id: UUID = Field(default_factory=uuid4, description="唯一标识")


class IntEntity(Entity[int]):
    """整数 ID 实体"""

    id: Optional[int] = Field(default=None, description="唯一标识")
