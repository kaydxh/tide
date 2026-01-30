#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Factory - Factory for creating TideDate entities

Similar to sea's date.entity.factory.go
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from ..kit.date import Repository as KitDateRepository
from .entity import TideDate


@dataclass
class FactoryConfig:
    """Factory configuration.

    Similar to sea's FactoryConfig struct.
    """

    date_repository: Optional[KitDateRepository] = None
    # validator: Optional[Any] = None  # Can add pydantic validator if needed

    def validate(self) -> None:
        """Validate factory configuration.

        Similar to sea's FactoryConfig.Validate method.
        """
        if self.date_repository is None:
            raise ValueError("date_repository is required")


# Type for factory config functions
FactoryConfigFunc = Callable[[FactoryConfig], None]


class DateFactory:
    """Factory for creating TideDate entities.

    Similar to sea's Factory struct.
    """

    def __init__(
        self,
        config: FactoryConfig,
        config_funcs: Optional[List[FactoryConfigFunc]] = None
    ):
        """Initialize factory.

        Similar to sea's NewFactory function.
        """
        # Apply config functions
        if config_funcs:
            for func in config_funcs:
                func(config)

        # Validate config
        config.validate()

        self._config = config

    def new_tide_date(self) -> TideDate:
        """Create a new TideDate entity.

        Similar to sea's Factory.NewSeaDate method.
        """
        return TideDate(date_repository=self._config.date_repository)
