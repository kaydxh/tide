#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Local Date Repository - 本地日期仓储实现
"""

from datetime import datetime

from ...domain.date.repository import (
    DateRepository,
    NowRequest,
    NowResponse,
    NowErrorRequest,
    NowErrorResponse,
)


class LocalDateRepository(DateRepository):
    """本地日期仓储实现。"""

    async def now(self, req: NowRequest) -> NowResponse:
        """获取当前日期/时间。"""
        return NowResponse(date=str(datetime.now()))

    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """获取当前日期/时间（带错误测试）。

        始终抛出异常用于测试。
        """
        raise Exception("Internal")
