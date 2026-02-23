#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Factory - Factory for creating TideDate entities
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from .repository import DateRepository
from .entity import TideDate


@dataclass
class FactoryConfig:
    """工厂配置。"""

    date_repository: Optional[DateRepository] = None

    def validate(self) -> None:
        """校验工厂配置。"""
        if self.date_repository is None:
            raise ValueError("date_repository is required")


# Type for factory config functions
FactoryConfigFunc = Callable[[FactoryConfig], None]


class DateFactory:
    """日期实体工厂。"""

    def __init__(
        self,
        config: FactoryConfig,
        config_funcs: Optional[List[FactoryConfigFunc]] = None
    ):
        """初始化工厂。"""
        # Apply config functions
        if config_funcs:
            for func in config_funcs:
                func(config)

        # Validate config
        config.validate()

        self._config = config

    def new_tide_date(self) -> TideDate:
        """创建 TideDate 实体。"""
        return TideDate(date_repository=self._config.date_repository)