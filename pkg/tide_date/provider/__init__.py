# -*- coding: utf-8 -*-
"""
Provider - Global dependency injection container

Similar to sea's provider package.
"""

from .provider import Provider, global_provider, get_sql_db, get_redis_db

__all__ = [
    "Provider",
    "global_provider",
    "get_sql_db",
    "get_redis_db",
]
