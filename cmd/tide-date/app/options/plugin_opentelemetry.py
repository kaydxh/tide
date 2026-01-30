#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: OpenTelemetry - Similar to sea's plugin.opentelemetry.go
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def install_opentelemetry(config: Dict[str, Any], web_server):
    """Install OpenTelemetry.

    Similar to sea's installOpenTelemetryOrDie.
    """
    if not config or not config.get("enabled", False):
        logger.debug("OpenTelemetry is disabled, skipping installation")
        return

    try:
        from tide.plugins.opentelemetry import OpenTelemetryPlugin

        plugin = OpenTelemetryPlugin()
        await plugin.install(config, web_server)

        logger.info("OpenTelemetry installed")

    except ImportError:
        logger.warning("OpenTelemetry dependencies not installed, skipping")
    except Exception as e:
        logger.error(f"Failed to install OpenTelemetry: {e}")
        raise
