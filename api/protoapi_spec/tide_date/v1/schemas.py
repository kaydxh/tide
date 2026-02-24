# -*- coding: utf-8 -*-
"""
tide_date v1 - Pydantic Schemas

由 scripts/gen_pydantic_models.py 从 api.proto 自动生成，请勿手动修改。
"""

from typing import Optional

from pydantic import BaseModel, Field

class Error(BaseModel):
    """通用错误结构"""

    code: int = Field(default=0, description="错误码")
    message: str = Field(default="", description="错误信息")
    reason: str = Field(default="", description="错误原因")

class NowRequest(BaseModel):
    """生成当前时间
  rpc Now(NowRequest) returns (NowResponse) {};
  rpc NowError(NowErrorRequest) returns (NowErrorResponse) {};
}"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    data: Optional[bytes] = Field(default=None, alias="Data")

    class Config:
        populate_by_name = True

class NowResponse(BaseModel):
    """NowResponse"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    date: str = Field(default="", alias="Date", description="当前时间")
    error: Optional[Error] = Field(default=None, alias="Error")

    class Config:
        populate_by_name = True

class NowErrorRequest(BaseModel):
    """NowErrorRequest"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")

    class Config:
        populate_by_name = True

class NowErrorResponse(BaseModel):
    """NowErrorResponse"""

    request_id: str = Field(default="", alias="RequestId", description="请求ID")
    date: str = Field(default="", alias="Date", description="当前时间")
    error: Optional[Error] = Field(default=None, alias="Error")

    class Config:
        populate_by_name = True
