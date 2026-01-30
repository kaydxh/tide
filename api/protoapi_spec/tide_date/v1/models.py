# -*- coding: utf-8 -*-
"""
Tide Date API v1 - Pydantic Models

对应 api.proto 中定义的消息结构
"""

from typing import Optional

from pydantic import BaseModel, Field


class Error(BaseModel):
    """通用错误结构"""

    code: int = Field(default=0, description="错误码")
    message: str = Field(default="", description="错误信息")
    reason: str = Field(default="", description="错误原因")


class NowRequest(BaseModel):
    """Now 请求"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    data: Optional[bytes] = Field(default=None, alias="Data", description="数据")

    class Config:
        populate_by_name = True


class NowResponse(BaseModel):
    """Now 响应"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    date: str = Field(default="", alias="Date", description="当前时间")
    error: Optional[Error] = Field(default=None, alias="Error", description="错误信息")

    class Config:
        populate_by_name = True


class NowErrorRequest(BaseModel):
    """NowError 请求"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")

    class Config:
        populate_by_name = True


class NowErrorResponse(BaseModel):
    """NowError 响应"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    date: str = Field(default="", alias="Date", description="当前时间")
    error: Optional[Error] = Field(default=None, alias="Error", description="错误信息")

    class Config:
        populate_by_name = True
