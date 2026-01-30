#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

TideDate Handler - Application handler for date operations

Similar to sea's seadate.command.application.go
"""

from ..domain.date import (
    DateFactory,
    NowRequest,
    NowResponse,
    NowErrorRequest,
    NowErrorResponse,
)


class TideDateHandler:
    """TideDate application handler.

    Similar to sea's SeaDateHandler struct.
    """

    def __init__(self, factory: DateFactory):
        """Initialize handler.

        Similar to sea's NewSeaDateHandler function.
        """
        self._factory = factory

    async def now(self, req: NowRequest) -> NowResponse:
        """Handle Now request.

        Similar to sea's SeaDateHandler.Now method.
        """
        handler = self._factory.new_tide_date()
        return await handler.now(req)

    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Handle NowError request.

        Similar to sea's SeaDateHandler.NowError method.
        """
        handler = self._factory.new_tide_date()
        return await handler.now_error(req)
