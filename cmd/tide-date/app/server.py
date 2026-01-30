#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...
"""

import asyncio
from pathlib import Path
from typing import Optional

import click

from .options import ServerRunOptions


def new_command():
    """Create a new click command with default parameters.

    Similar to sea's NewCommand using cobra.
    """

    @click.command()
    @click.option(
        "--config", "-c",
        type=click.Path(exists=True),
        default="./conf/tide-date.yaml",
        help="Path to configuration file"
    )
    @click.option(
        "--version", "-v",
        is_flag=True,
        help="Show version and exit"
    )
    def command(config: str, version: bool):
        """Tide Date Service - A Python web service framework."""
        if version:
            from tide import __version__
            click.echo(f"tide-date version {__version__}")
            return

        run_command(config)

    return command


def run_command(config_file: str):
    """Run the server with the given configuration.

    Similar to sea's runCommand function.
    """
    options = ServerRunOptions(config_file)

    # Complete options (set defaults)
    completed_options = options.complete()

    # Run the server
    asyncio.run(completed_options.run())
