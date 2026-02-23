#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Entity - Domain entity for date operations

Similar to sea's date.entity.go
"""

import logging
from dataclasses import dataclass
from typing import Optional

from ..kit.date import Repository as KitDateRepository
from ..kit.date import NowRequest as KitNowRequest
from ..kit.date import NowErrorRequest as KitNowErrorRequest
from .error import ErrInternal

# 从 peek gRPC 拦截器中获取 request_id 和 trace_id
try:
    from peek.net.grpc.interceptor import get_request_id, get_trace_id
except ImportError:
    def get_request_id():
        return None
    def get_trace_id():
        return ""

logger = logging.getLogger(__name__)


def _log_prefix() -> str:
    """生成日志前缀，包含 request_id 和 trace_id"""
    parts = []
    request_id = get_request_id()
    if request_id:
        parts.append(f"[{request_id}]")
    trace_id = get_trace_id()
    if trace_id:
        parts.append(f"[trace_id={trace_id}]")
    return " ".join(parts) + " " if parts else ""


@dataclass
class NowRequest:
    """Now request."""

    request_id: str = ""


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


class TideDate:
    """TideDate entity.

    Similar to sea's SeaDate struct.
    """

    def __init__(self, date_repository: KitDateRepository):
        self.date_repository = date_repository

    async def now(self, req: NowRequest) -> NowResponse:
        """Get current date/time.

        Similar to sea's SeaDate.Now method.
        """
        try:
            kit_req = KitNowRequest()
            kit_resp = await self.date_repository.now(kit_req)

            return NowResponse(date=kit_resp.date)

        except Exception as e:
            logger.error(f"{_log_prefix()}failed to call Now, err: {e}")
            raise ErrInternal(str(e)) from e

    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Get current date/time with error.

        Similar to sea's SeaDate.NowError method.
        """
        try:
            kit_req = KitNowErrorRequest(request_id=req.request_id)
            kit_resp = await self.date_repository.now_error(kit_req)

            return NowErrorResponse(date=kit_resp.date)

        except Exception as e:
            logger.error(f"{_log_prefix()}failed to call NowError, err: {e}")
            raise ErrInternal(str(e)) from e
