#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Provider - Global dependency injection container

Similar to sea's provider.go
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Provider:
    """Provider for global instance.

    Similar to sea's Provider struct.
    """

    config: Dict[str, Any] = field(default_factory=dict)
    mysql: Optional[Any] = None  # SQLAlchemy session or connection
    redis: Optional[Any] = None  # Redis client
    resolver_service: Optional[Any] = None


# Global singleton instance
_provider = Provider()


def global_provider() -> Provider:
    """Get global provider instance.

    Similar to sea's GlobalProvider().
    """
    return _provider


def get_sql_db():
    """Get SQL database connection.

    Similar to sea's GetSqlDB().
    """
    return _provider.mysql


def get_redis_db():
    """Get Redis database connection.

    Similar to sea's GetRedisDB().
    """
    return _provider.redis


def get_resolver_service():
    """Get resolver service.

    Similar to sea's GetResolverService().
    """
    return _provider.resolver_service
