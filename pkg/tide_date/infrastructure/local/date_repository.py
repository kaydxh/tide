#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Local Date Repository - Local implementation of date repository

Similar to sea's local.date.repository.go
"""

from datetime import datetime

from ...domain.kit.date import (
    Repository,
    NowRequest,
    NowResponse,
    NowErrorRequest,
    NowErrorResponse,
)


class LocalDateRepository(Repository):
    """Local implementation of date repository.

    Similar to sea's Repository struct in infrastructure/local.
    """

    async def now(self, req: NowRequest) -> NowResponse:
        """Get current date/time.

        Similar to sea's Repository.Now method.
        """
        return NowResponse(date=str(datetime.now()))

    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Get current date/time with error.

        Similar to sea's Repository.NowError method.
        Always raises an error for testing purposes.
        """
        raise Exception("Internal")
