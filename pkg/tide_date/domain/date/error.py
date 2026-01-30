#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
...

Date Domain Errors

Similar to sea's date.entity.error.go
"""


class DateDomainError(Exception):
    """Base exception for date domain errors."""

    pass


class ErrInternal(DateDomainError):
    """Internal error."""

    def __init__(self, message: str = "Internal error"):
        super().__init__(message)
        self.message = message
