#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Root Router - Web handlers setup

Similar to sea's root.router.go
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from web.modules.tidedate import DateController


def new_web_handlers(web_server, controller: "DateController"):
    """Setup web handlers.

    Similar to sea's NewWebHandlers function.
    """
    # Add post start hook to install web handlers
    async def install_handlers():
        controller.register_routes(web_server)

    web_server.add_post_start_hook("web_handler", install_handlers)

    return [controller]
