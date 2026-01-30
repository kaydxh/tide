#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ValueObject - 值对象基类

值对象是不可变的，通过其属性值来定义相等性
"""

from typing import Any

from pydantic import BaseModel


class ValueObject(BaseModel):
    """
    值对象基类

    值对象的特点：
    - 不可变（immutable）
    - 无唯一标识
    - 通过属性值比较相等性
    - 可以被替换
    """

    class Config:
        """Pydantic 配置"""
        frozen = True  # 不可变

    def __eq__(self, other: Any) -> bool:
        """值对象相等性比较（基于所有属性）"""
        if not isinstance(other, self.__class__):
            return False
        return self.model_dump() == other.model_dump()

    def __hash__(self) -> int:
        """哈希值"""
        return hash(tuple(sorted(self.model_dump().items())))


# 常用值对象示例


class Money(ValueObject):
    """金额值对象"""

    amount: float
    currency: str = "CNY"

    def add(self, other: "Money") -> "Money":
        """加法"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        """减法"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: float) -> "Money":
        """乘法"""
        return Money(amount=self.amount * factor, currency=self.currency)


class Address(ValueObject):
    """地址值对象"""

    country: str = "中国"
    province: str = ""
    city: str = ""
    district: str = ""
    street: str = ""
    postal_code: str = ""

    @property
    def full_address(self) -> str:
        """完整地址"""
        parts = [
            self.country,
            self.province,
            self.city,
            self.district,
            self.street,
        ]
        return "".join(filter(None, parts))


class DateRange(ValueObject):
    """日期范围值对象"""

    from datetime import datetime

    start: datetime
    end: datetime

    def contains(self, dt: datetime) -> bool:
        """是否包含指定日期"""
        return self.start <= dt <= self.end

    def overlaps(self, other: "DateRange") -> bool:
        """是否与另一个范围重叠"""
        return self.start <= other.end and other.start <= self.end

    @property
    def duration_days(self) -> int:
        """持续天数"""
        return (self.end - self.start).days
