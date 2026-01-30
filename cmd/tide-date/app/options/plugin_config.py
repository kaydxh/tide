#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Config - Similar to sea's plugin.config.go
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def install_config(config: Dict[str, Any]):
    """Install configuration to global provider.

    Similar to sea's installConfigOrDie.
    """
    from pkg.tide_date.provider import global_provider

    provider = global_provider()
    provider.config = config

    logger.info(f"Config installed: {list(config.keys())}")
