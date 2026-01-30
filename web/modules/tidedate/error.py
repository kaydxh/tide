#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Controller Error Handling

Similar to sea's date.controller.error.go
"""

from typing import Union

from api.protoapi_spec.tide_date.v1 import Error


def api_error(err: Exception) -> Error:
    """Convert exception to API error.

    Similar to sea's APIError function.
    """
    return Error(
        code=500,
        message=str(err),
        reason="Internal Server Error",
    )
