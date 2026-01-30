#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Controller - HTTP/gRPC handlers for date service

Similar to sea's date.controller.go and date.router.go
"""

import logging
from typing import TYPE_CHECKING

from api.protoapi_spec.tide_date.v1 import (
    NowRequest,
    NowResponse,
    NowErrorRequest,
    NowErrorResponse,
)
from pkg.tide_date.domain.date import (
    NowRequest as DomainNowRequest,
    NowErrorRequest as DomainNowErrorRequest,
)
from .error import api_error

if TYPE_CHECKING:
    from pkg.tide_date.application import Application

logger = logging.getLogger(__name__)


class DateController:
    """Date service controller.

    Similar to sea's Controller struct.

    Handles HTTP routes and calls application layer handlers.
    """

    def __init__(self, app: "Application"):
        """Initialize controller.

        Similar to sea's NewController function.
        """
        self._app = app

    def register_routes(self, web_server):
        """Register routes to web server.

        Similar to sea's SetRoutes method.

        Args:
            web_server: GenericWebServer or FallbackWebServer instance
        """
        # 获取 FastAPI app - 支持 GenericWebServer 和 FallbackWebServer
        app = getattr(web_server, 'app', None)
        if app is None:
            # 尝试获取 router（兼容 FallbackWebServer）
            router = getattr(web_server, 'router', None)
            if router is None:
                raise AttributeError("web_server must have 'app' or 'router' attribute")
            app = router

        @app.get("/Now")
        @app.post("/Now")
        async def now(request: NowRequest = None):
            """Get current date/time.

            curl -X POST http://localhost:10001/Now \
              -H "Content-Type: application/json" \
              -d '{"RequestId": "test-123"}'
            """
            return await self.now(request or NowRequest())

        @app.get("/NowError")
        @app.post("/NowError")
        async def now_error(request: NowErrorRequest = None):
            """Get current date/time with error."""
            return await self.now_error(request or NowErrorRequest())

    async def now(self, req: NowRequest) -> NowResponse:
        """Handle Now request.

        Similar to sea's Controller.Now method.
        """
        try:
            domain_req = DomainNowRequest(request_id=req.request_id)
            domain_resp = await self._app.commands.tide_date_handler.now(domain_req)

            return NowResponse(
                request_id=req.request_id,
                date=domain_resp.date,
            )

        except Exception as e:
            logger.error(f"failed to run [Now] command: {e}")
            return NowResponse(
                request_id=req.request_id,
                error=api_error(e),
            )

    async def now_error(self, req: NowErrorRequest) -> NowErrorResponse:
        """Handle NowError request.

        Similar to sea's Controller.NowError method.
        """
        try:
            domain_req = DomainNowErrorRequest(request_id=req.request_id)
            domain_resp = await self._app.commands.tide_date_handler.now_error(
                domain_req
            )

            return NowErrorResponse(
                request_id=req.request_id,
                date=domain_resp.date,
            )

        except Exception as e:
            logger.error(f"failed to run [NowError] command: {e}")
            return NowErrorResponse(
                request_id=req.request_id,
                error=api_error(e),
            )
