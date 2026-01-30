#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Kit Repository - Low-level date repository interface

Similar to sea's domain/kit/date/date.repository.go
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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


class Repository(ABC):
    """Date repository interface.

    Similar to sea's Repository interface in domain/kit/date.
    """

    @abstractmethod
    async def now(self, req: NowRequest) -> NowResponse:
        """Get current date/time."""
        pass

    @abstractmethod
    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Get current date/time with error."""
        pass
