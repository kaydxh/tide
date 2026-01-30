#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Repository Interface

Similar to sea's date.entity.repository.go
"""

from abc import ABC, abstractmethod

from .entity import NowRequest, NowResponse, NowErrorRequest, NowErrorResponse


class DateRepository(ABC):
    """Date repository interface.

    Similar to sea's Repository interface in domain/date.
    """

    @abstractmethod
    async def now(self, req: NowRequest) -> NowResponse:
        """Get current date/time."""
        pass

    @abstractmethod
    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Get current date/time with error."""
        pass
