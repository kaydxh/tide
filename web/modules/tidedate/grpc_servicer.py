#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TideDate gRPC Servicer

实现 proto 定义的 TideDateServiceServicer 接口，
将 gRPC 请求转发给 DateController 处理。
"""

import asyncio
import logging
from typing import TYPE_CHECKING

import grpc

from pkg.tide_date.domain.date import (
    NowRequest as DomainNowRequest,
    NowErrorRequest as DomainNowErrorRequest,
)

# 从 peek gRPC 拦截器中获取 request_id 和 trace_id
try:
    from peek.net.grpc.interceptor import get_request_id, get_trace_id
except ImportError:
    def get_request_id():
        return None
    def get_trace_id():
        return ""

if TYPE_CHECKING:
    from pkg.tide_date.application import Application

logger = logging.getLogger(__name__)


def _log_prefix() -> str:
    """生成日志前缀，包含 request_id 和 trace_id"""
    parts = []
    request_id = get_request_id()
    if request_id:
        parts.append(f"[{request_id}]")
    trace_id = get_trace_id()
    if trace_id:
        parts.append(f"[trace_id={trace_id}]")
    return " ".join(parts) + " " if parts else ""


def _load_grpc_modules():
    """
    动态加载 protobuf/gRPC 生成的模块。

    由于 proto 生成代码中 `from types import error_pb2` 与 Python 标准库
    的 types 模块冲突，需要通过 importlib 手动加载。
    """
    import importlib
    import importlib.util
    import sys
    import types as std_types
    import os

    base_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "api", "protoapi_spec"
    )
    base_dir = os.path.normpath(base_dir)

    # 如果已经加载过，直接返回
    if "tide_date.v1.api_pb2" in sys.modules and "tide_date.v1.api_pb2_grpc" in sys.modules:
        return sys.modules["tide_date.v1.api_pb2"], sys.modules["tide_date.v1.api_pb2_grpc"]

    # 1. 注入 types.error_pb2（避免与标准库 types 冲突）
    if "types.error_pb2" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "types.error_pb2", os.path.join(base_dir, "types", "error_pb2.py")
        )
        error_pb2 = importlib.util.module_from_spec(spec)
        sys.modules["types.error_pb2"] = error_pb2
        spec.loader.exec_module(error_pb2)

    # 2. 创建 tide_date 和 tide_date.v1 包
    if "tide_date" not in sys.modules:
        tide_date_pkg = std_types.ModuleType("tide_date")
        tide_date_pkg.__path__ = [os.path.join(base_dir, "tide_date")]
        sys.modules["tide_date"] = tide_date_pkg

    if "tide_date.v1" not in sys.modules:
        tide_date_v1_pkg = std_types.ModuleType("tide_date.v1")
        tide_date_v1_pkg.__path__ = [os.path.join(base_dir, "tide_date", "v1")]
        sys.modules["tide_date.v1"] = tide_date_v1_pkg

    # 3. 加载 api_pb2
    if "tide_date.v1.api_pb2" not in sys.modules:
        spec2 = importlib.util.spec_from_file_location(
            "tide_date.v1.api_pb2",
            os.path.join(base_dir, "tide_date", "v1", "api_pb2.py"),
        )
        api_pb2 = importlib.util.module_from_spec(spec2)
        sys.modules["tide_date.v1.api_pb2"] = api_pb2
        sys.modules["tide_date.v1"].api_pb2 = api_pb2
        spec2.loader.exec_module(api_pb2)
    else:
        api_pb2 = sys.modules["tide_date.v1.api_pb2"]

    # 4. 加载 api_pb2_grpc
    if "tide_date.v1.api_pb2_grpc" not in sys.modules:
        spec3 = importlib.util.spec_from_file_location(
            "tide_date.v1.api_pb2_grpc",
            os.path.join(base_dir, "tide_date", "v1", "api_pb2_grpc.py"),
        )
        api_pb2_grpc = importlib.util.module_from_spec(spec3)
        sys.modules["tide_date.v1.api_pb2_grpc"] = api_pb2_grpc
        spec3.loader.exec_module(api_pb2_grpc)
    else:
        api_pb2_grpc = sys.modules["tide_date.v1.api_pb2_grpc"]

    return api_pb2, api_pb2_grpc


# 预加载模块
api_pb2, api_pb2_grpc = _load_grpc_modules()


class TideDateGRPCServicer(api_pb2_grpc.TideDateServiceServicer):
    """
    gRPC Servicer 实现。

    将 gRPC 请求转发给 Application 层处理，
    类似 HTTP controller 中的 now/now_error 方法。
    """

    def __init__(self, app: "Application"):
        self._app = app

    def Now(self, request, context):
        """处理 Now gRPC 请求"""
        try:
            domain_req = DomainNowRequest(request_id=request.request_id)
            # 在 gRPC 线程中运行异步代码
            loop = asyncio.new_event_loop()
            try:
                domain_resp = loop.run_until_complete(
                    self._app.commands.tide_date_handler.now(domain_req)
                )
            finally:
                loop.close()

            return api_pb2.NowResponse(
                request_id=request.request_id,
                date=domain_resp.date,
            )

        except Exception as e:
            logger.error(f"{_log_prefix()}gRPC [Now] failed: {e}")
            return api_pb2.NowResponse(
                request_id=request.request_id,
                error=api_pb2.DESCRIPTOR.dependencies[1].message_types_by_name[
                    "Error"
                ]._concrete_class(
                    code=500,
                    message=str(e),
                    reason="Internal Server Error",
                )
                if False
                else _make_error(500, str(e)),
            )

    def NowError(self, request, context):
        """处理 NowError gRPC 请求"""
        try:
            domain_req = DomainNowErrorRequest(request_id=request.request_id)
            loop = asyncio.new_event_loop()
            try:
                domain_resp = loop.run_until_complete(
                    self._app.commands.tide_date_handler.now_error(domain_req)
                )
            finally:
                loop.close()

            return api_pb2.NowErrorResponse(
                request_id=request.request_id,
                date=domain_resp.date,
            )

        except Exception as e:
            logger.error(f"{_log_prefix()}gRPC [NowError] failed: {e}")
            return api_pb2.NowErrorResponse(
                request_id=request.request_id,
                error=_make_error(500, str(e)),
            )


def _make_error(code: int, message: str):
    """构造 protobuf Error 对象"""
    from types import error_pb2 as types_error_pb2
    return types_error_pb2.Error(
        code=code,
        message=message,
        reason="Internal Server Error",
    )


def register_grpc_servicer(web_server, app: "Application"):
    """
    将 gRPC Servicer 注册到 GenericWebServer。

    Args:
        web_server: GenericWebServer 实例
        app: Application 实例
    """
    servicer = TideDateGRPCServicer(app)

    web_server.register_grpc_service(
        lambda server: api_pb2_grpc.add_TideDateServiceServicer_to_server(
            servicer, server
        ),
        service_name="tide.api.tidedate.TideDateService",
    )

    logger.info("gRPC TideDateService servicer registered")
