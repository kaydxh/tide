#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Local Date Repository - 本地日期仓储实现
"""

from datetime import datetime

from ..domain.date.repository import (
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
