#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Application - Application layer entry point

Similar to sea's application.go
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tide_date_handler import TideDateHandler


@dataclass
class Commands:
    """Application commands container.

    Similar to sea's Commands struct.
    """

    tide_date_handler: "TideDateHandler" = None


@dataclass
class Application:
    """Application layer entry point.

    Similar to sea's Application struct.
    """

    commands: Commands = None
