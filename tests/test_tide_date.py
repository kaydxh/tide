# -*- coding: utf-8 -*-
"""tide-date 服务集成测试

真实调用已启动的 tide-date 服务，走完整网络链路。
需要先启动服务：
    python cmd/tide-date/main.py -c conf/tide-date.yaml

测试包含：
  1. HTTP 测试（localhost:10001）
  2. gRPC 测试（localhost:10002，需要配置 grpc.enabled=true, grpc.port=10002）

运行测试命令：
    # 运行全部测试
    python -m pytest tests/test_tide_date.py -v
    # 只运行 gRPC 测试
    python -m pytest tests/test_tide_date.py -v -k "Grpc" -s
    # 只运行 HTTP 测试
    python -m pytest tests/test_tide_date.py -v -k "not Grpc"
"""

import json
from datetime import datetime

import httpx
import pytest

# 服务地址，与 conf/tide-date.yaml 中 web.bind_address 一致
TIDE_DATE_SERVICE_URL = "http://localhost:10001"


@pytest.fixture
async def client():
    """创建连接到真实 tide-date 服务的 httpx.AsyncClient"""
    async with httpx.AsyncClient(
        base_url=TIDE_DATE_SERVICE_URL,
        timeout=httpx.Timeout(10.0),
    ) as c:
        yield c


def _check_service_available():
    """检查 tide-date 服务是否可用，不可用则跳过测试"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 10001))
        if result != 0:
            pytest.skip(
                f"tide-date 服务未启动 (localhost:10001)，"
                f"请先运行: python cmd/tide-date/main.py -c conf/tide-date.yaml"
            )
    finally:
        sock.close()


@pytest.fixture(autouse=False)
def require_service():
    """前置检查：tide-date 服务必须可用"""
    _check_service_available()


class TestNow:
    """调用 tide-date 服务的 /Now 接口测试"""

    pytestmark = pytest.mark.usefixtures("require_service")

    async def test_post_now(self, client: httpx.AsyncClient):
        """POST /Now 带 RequestId，验证返回当前日期"""
        resp = await client.post("/Now", json={"RequestId": "test_001"})
        print(f"\n[POST /Now] status={resp.status_code}, body={resp.text}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["RequestId"] == "test_001"
        assert data["Error"] is None
        assert data["Date"] != ""
        # 验证返回的是合法的 datetime 格式
        parsed = datetime.fromisoformat(data["Date"])
        assert parsed.year >= 2024

    async def test_get_now(self, client: httpx.AsyncClient):
        """GET /Now 验证返回当前日期"""
        resp = await client.get("/Now")
        print(f"\n[GET /Now] status={resp.status_code}, body={resp.text}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["Error"] is None
        assert data["Date"] != ""
        parsed = datetime.fromisoformat(data["Date"])
        assert parsed.year >= 2024

    async def test_post_now_empty_body(self, client: httpx.AsyncClient):
        """POST /Now 空请求体"""
        resp = await client.post("/Now", json={})
        print(f"\n[POST /Now empty] status={resp.status_code}, body={resp.text}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["Error"] is None
        assert data["Date"] != ""

    async def test_post_now_multiple_calls(self, client: httpx.AsyncClient):
        """连续多次调用 POST /Now"""
        for i in range(3):
            resp = await client.post("/Now", json={"RequestId": f"batch_{i}"})
            print(f"\n[POST /Now batch_{i}] status={resp.status_code}, body={resp.text}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["RequestId"] == f"batch_{i}"
            assert data["Error"] is None
            assert data["Date"] != ""


class TestNowError:
    """调用 tide-date 服务的 /NowError 接口测试"""

    pytestmark = pytest.mark.usefixtures("require_service")

    async def test_post_now_error(self, client: httpx.AsyncClient):
        """POST /NowError 验证返回业务层 500 错误"""
        resp = await client.post("/NowError", json={"RequestId": "test_err_001"})
        print(f"\n[POST /NowError] status={resp.status_code}, body={resp.text}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["RequestId"] == "test_err_001"
        assert data["Error"] is not None
        assert data["Error"]["code"] == 500
        assert "Internal" in data["Error"]["message"]

    async def test_get_now_error(self, client: httpx.AsyncClient):
        """GET /NowError 验证返回错误"""
        resp = await client.get("/NowError")
        print(f"\n[GET /NowError] status={resp.status_code}, body={resp.text}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["Error"] is not None
        assert data["Error"]["code"] == 500


# ============================================================================
# gRPC 测试
# ============================================================================

# gRPC 服务地址，与 conf/tide-date.yaml 中 grpc.port 一致
TIDE_DATE_GRPC_ADDRESS = "localhost:10002"


def _load_grpc_pb2():
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

    base_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "api", "protoapi_spec")
    )

    # 如果已经加载过，直接返回
    if (
        "tide_date.v1.api_pb2" in sys.modules
        and "tide_date.v1.api_pb2_grpc" in sys.modules
    ):
        return sys.modules["tide_date.v1.api_pb2"], sys.modules["tide_date.v1.api_pb2_grpc"]

    # 1. 注入 types.error_pb2
    if "types.error_pb2" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "types.error_pb2", os.path.join(base_dir, "types", "error_pb2.py")
        )
        error_pb2 = importlib.util.module_from_spec(spec)
        sys.modules["types.error_pb2"] = error_pb2
        spec.loader.exec_module(error_pb2)

    # 2. 创建 tide_date / tide_date.v1 虚拟包
    if "tide_date" not in sys.modules:
        pkg = std_types.ModuleType("tide_date")
        pkg.__path__ = [os.path.join(base_dir, "tide_date")]
        sys.modules["tide_date"] = pkg

    if "tide_date.v1" not in sys.modules:
        v1_pkg = std_types.ModuleType("tide_date.v1")
        v1_pkg.__path__ = [os.path.join(base_dir, "tide_date", "v1")]
        sys.modules["tide_date.v1"] = v1_pkg

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

    # 4. 加载 api_pb2_grpc
    if "tide_date.v1.api_pb2_grpc" not in sys.modules:
        spec3 = importlib.util.spec_from_file_location(
            "tide_date.v1.api_pb2_grpc",
            os.path.join(base_dir, "tide_date", "v1", "api_pb2_grpc.py"),
        )
        api_pb2_grpc = importlib.util.module_from_spec(spec3)
        sys.modules["tide_date.v1.api_pb2_grpc"] = api_pb2_grpc
        spec3.loader.exec_module(api_pb2_grpc)

    return sys.modules["tide_date.v1.api_pb2"], sys.modules["tide_date.v1.api_pb2_grpc"]


def _check_grpc_service_available():
    """检查 gRPC 服务是否可用，不可用则跳过测试"""
    import grpc
    channel = grpc.insecure_channel(TIDE_DATE_GRPC_ADDRESS)
    try:
        grpc.channel_ready_future(channel).result(timeout=2)
    except grpc.FutureTimeoutError:
        pytest.skip(
            f"tide-date gRPC 服务未启动 ({TIDE_DATE_GRPC_ADDRESS})，"
            f"请先运行: python cmd/tide-date/main.py -c conf/tide-date.yaml "
            f"(确保配置 grpc.enabled=true, grpc.port=10002)"
        )
    finally:
        channel.close()


@pytest.fixture(autouse=False)
def require_grpc_service():
    """前置检查：gRPC 服务必须可用"""
    _check_grpc_service_available()


@pytest.fixture
def grpc_stub():
    """创建连接到真实 tide-date gRPC 服务的 Stub"""
    import grpc
    api_pb2, api_pb2_grpc = _load_grpc_pb2()
    channel = grpc.insecure_channel(TIDE_DATE_GRPC_ADDRESS)
    stub = api_pb2_grpc.TideDateServiceStub(channel)
    yield stub, api_pb2
    channel.close()


class TestGrpcNow:
    """gRPC 调用 tide-date 服务的 Now 接口测试"""

    pytestmark = pytest.mark.usefixtures("require_grpc_service")

    def test_grpc_now(self, grpc_stub):
        """gRPC Now 带 request_id，验证返回当前日期"""
        stub, api_pb2 = grpc_stub
        request = api_pb2.NowRequest(request_id="grpc_test_001")
        response = stub.Now(request)
        print(f"\n[gRPC Now] response: request_id={response.request_id}, date={response.date}, has_error={response.HasField('error') if True else False}")

        assert response.request_id == "grpc_test_001"
        assert response.date != ""
        # 验证返回的是合法的 datetime 格式
        parsed = datetime.fromisoformat(response.date)
        assert parsed.year >= 2024
        # 无错误
        assert not response.HasField("error")

    def test_grpc_now_empty_request(self, grpc_stub):
        """gRPC Now 空请求（拦截器会自动生成 request_id）"""
        stub, api_pb2 = grpc_stub
        request = api_pb2.NowRequest()
        response = stub.Now(request)
        print(f"\n[gRPC Now empty] response: request_id='{response.request_id}', date={response.date}")

        # RequestIDInterceptor 会自动为空请求生成 UUID
        assert response.request_id != ""
        assert response.date != ""
        parsed = datetime.fromisoformat(response.date)
        assert parsed.year >= 2024

    def test_grpc_now_multiple_calls(self, grpc_stub):
        """gRPC Now 连续多次调用"""
        stub, api_pb2 = grpc_stub
        for i in range(3):
            request = api_pb2.NowRequest(request_id=f"grpc_batch_{i}")
            response = stub.Now(request)
            print(f"\n[gRPC Now batch_{i}] response: request_id={response.request_id}, date={response.date}")
            assert response.request_id == f"grpc_batch_{i}"
            assert response.date != ""


class TestGrpcNowError:
    """gRPC 调用 tide-date 服务的 NowError 接口测试"""

    pytestmark = pytest.mark.usefixtures("require_grpc_service")

    def test_grpc_now_error(self, grpc_stub):
        """gRPC NowError 验证返回业务层错误"""
        stub, api_pb2 = grpc_stub
        request = api_pb2.NowErrorRequest(request_id="grpc_err_001")
        response = stub.NowError(request)
        print(f"\n[gRPC NowError] response: request_id={response.request_id}, error_code={response.error.code}, error_message={response.error.message}")

        assert response.request_id == "grpc_err_001"
        assert response.HasField("error")
        assert response.error.code == 500
        assert "Internal" in response.error.message

    def test_grpc_now_error_empty_request(self, grpc_stub):
        """gRPC NowError 空请求（拦截器会自动生成 request_id）"""
        stub, api_pb2 = grpc_stub
        request = api_pb2.NowErrorRequest()
        response = stub.NowError(request)
        print(f"\n[gRPC NowError empty] response: request_id='{response.request_id}', error_code={response.error.code}, error_message={response.error.message}")

        # RequestIDInterceptor 会自动为空请求生成 UUID
        assert response.request_id != ""
        assert response.HasField("error")
        assert response.error.code == 500