#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Repository Interface - 日期仓储接口定义

合并了原 domain/kit/date/repository.py 的底层接口，
消除了 kit 中间层的冗余抽象。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NowRequest:
    """Now request."""

    pass


@dataclass
class NowResponse:
    """Now response."""

    date: str = ""


@dataclass
class NowErrorRequest:
    """NowError request."""

    request_id: str = ""


@dataclass
class NowErrorResponse:
    """NowError response."""

    date: str = ""


class DateRepository(ABC):
    """日期仓储抽象接口。

    由 infrastructure 层实现。
    """

    @abstractmethod
    async def now(self, req: NowRequest) -> NowResponse:
        """获取当前日期/时间。"""
        pass

    @abstractmethod
    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """获取当前日期/时间（带错误测试）。"""
        pass