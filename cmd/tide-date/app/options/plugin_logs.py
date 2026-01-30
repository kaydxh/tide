#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Logs - Similar to sea's plugin.logs.go
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from .options import LogConfig

logger = logging.getLogger(__name__)


def install_logs(config: Optional[LogConfig]):
    """Install logging configuration.

    Similar to sea's installLogsOrDie.
    """
    if config is None:
        config = LogConfig()

    # Set log level
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "fatal": logging.CRITICAL,
    }
    level = level_map.get(config.level.lower(), logging.DEBUG)

    # Create formatter
    if config.formatter == "glog":
        # Google log format
        fmt = "%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s"
        datefmt = "%m%d %H:%M:%S"
    else:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add handlers based on redirect config
    if config.redirect == "stdout" or config.redirect == "":
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    else:
        # File handler
        log_path = Path(config.filepath)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "tide-date.log"

        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.rotate_size,
            backupCount=config.max_count,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logger.info(f"Logging initialized with level: {config.level}")
