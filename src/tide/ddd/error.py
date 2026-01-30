#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
领域错误定义

参考 Go 版本 sea 的 domain/date/date.entity.error.go 实现
"""

from typing import Any, Dict, Optional


class DomainError(Exception):
    """
    领域错误基类

    所有领域层错误应继承此类
    """

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化领域错误

        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class EntityNotFoundError(DomainError):
    """
    实体不存在错误

    当查找的实体不存在时抛出
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        """
        初始化实体不存在错误

        Args:
            entity_type: 实体类型
            entity_id: 实体 ID
            message: 错误消息
        """
        msg = message or f"{entity_type} with id '{entity_id}' not found"
        super().__init__(
            message=msg,
            code="ENTITY_NOT_FOUND",
            details={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
            },
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class ValidationError(DomainError):
    """
    验证错误

    当数据验证失败时抛出
    """

    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None,
    ):
        """
        初始化验证错误

        Args:
            field: 字段名
            message: 错误消息
            value: 字段值
        """
        super().__init__(
            message=f"Validation failed for field '{field}': {message}",
            code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": str(value) if value is not None else None,
            },
        )
        self.field = field
        self.value = value


class BusinessRuleViolationError(DomainError):
    """
    业务规则违反错误

    当违反业务规则时抛出
    """

    def __init__(
        self,
        rule: str,
        message: str,
    ):
        """
        初始化业务规则错误

        Args:
            rule: 规则名称
            message: 错误消息
        """
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            details={"rule": rule},
        )
        self.rule = rule


class ConcurrencyError(DomainError):
    """
    并发错误

    当发生并发冲突时抛出（如乐观锁失败）
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        expected_version: int,
        actual_version: int,
    ):
        """
        初始化并发错误

        Args:
            entity_type: 实体类型
            entity_id: 实体 ID
            expected_version: 期望版本
            actual_version: 实际版本
        """
        super().__init__(
            message=(
                f"Concurrency conflict for {entity_type} '{entity_id}': "
                f"expected version {expected_version}, got {actual_version}"
            ),
            code="CONCURRENCY_ERROR",
            details={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "expected_version": expected_version,
                "actual_version": actual_version,
            },
        )
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version
