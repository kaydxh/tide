# -*- coding: utf-8 -*-
"""
Tide Date API v1 Protocol Definitions

This module contains the generated Python classes from proto definitions.
For Python, we also provide Pydantic models for HTTP/JSON APIs.
"""

from .models import (
    NowRequest,
    NowResponse,
    NowErrorRequest,
    NowErrorResponse,
    Error,
)

__all__ = [
    "NowRequest",
    "NowResponse",
    "NowErrorRequest",
    "NowErrorResponse",
    "Error",
]
