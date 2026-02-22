# -*- coding: utf-8 -*-
"""tide-date 单元测试

覆盖 DDD 各层：
- API 模型层：NowRequest/NowResponse/NowErrorRequest/NowErrorResponse/Error
- Domain 层：TideDate 实体、DateFactory 工厂、领域错误
- Application 层：TideDateHandler
- Infrastructure 层：LocalDateRepository
- Web 层：DateController（路由注册、now/now_error 接口）
- Plugin 层：install_web_handler
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ========== API 模型层测试 ==========


class TestApiModels:
    """API Pydantic 模型测试"""

    def test_now_request_default(self):
        """测试 NowRequest 默认值"""
        from api.protoapi_spec.tide_date.v1 import NowRequest

        req = NowRequest()
        assert req.request_id == ""
        assert req.data is None

    def test_now_request_with_alias(self):
        """测试 NowRequest 通过别名赋值"""
        from api.protoapi_spec.tide_date.v1 import NowRequest

        req = NowRequest(RequestId="req_001", Data=b"hello")
        assert req.request_id == "req_001"
        assert req.data == b"hello"

    def test_now_request_with_field_name(self):
        """测试 NowRequest 通过字段名赋值（populate_by_name）"""
        from api.protoapi_spec.tide_date.v1 import NowRequest

        req = NowRequest(request_id="req_002")
        assert req.request_id == "req_002"

    def test_now_response_default(self):
        """测试 NowResponse 默认值"""
        from api.protoapi_spec.tide_date.v1 import NowResponse

        resp = NowResponse()
        assert resp.request_id == ""
        assert resp.date == ""
        assert resp.error is None

    def test_now_response_with_error(self):
        """测试 NowResponse 带错误信息"""
        from api.protoapi_spec.tide_date.v1 import Error, NowResponse

        err = Error(code=500, message="内部错误", reason="Internal Server Error")
        resp = NowResponse(request_id="req_001", date="", error=err)
        assert resp.error.code == 500
        assert resp.error.message == "内部错误"

    def test_now_response_with_date(self):
        """测试 NowResponse 带日期"""
        from api.protoapi_spec.tide_date.v1 import NowResponse

        resp = NowResponse(request_id="req_001", date="2024-01-01 12:00:00")
        assert resp.date == "2024-01-01 12:00:00"
        assert resp.error is None

    def test_now_error_request_default(self):
        """测试 NowErrorRequest 默认值"""
        from api.protoapi_spec.tide_date.v1 import NowErrorRequest

        req = NowErrorRequest()
        assert req.request_id == ""

    def test_now_error_response_with_error(self):
        """测试 NowErrorResponse 带错误"""
        from api.protoapi_spec.tide_date.v1 import Error, NowErrorResponse

        err = Error(code=500, message="模拟错误", reason="Internal Server Error")
        resp = NowErrorResponse(request_id="req_001", error=err)
        assert resp.error is not None
        assert resp.error.code == 500

    def test_error_model_default(self):
        """测试 Error 模型默认值"""
        from api.protoapi_spec.tide_date.v1 import Error

        err = Error()
        assert err.code == 0
        assert err.message == ""
        assert err.reason == ""

    def test_now_response_json_serialization(self):
        """测试 NowResponse JSON 序列化"""
        from api.protoapi_spec.tide_date.v1 import NowResponse

        resp = NowResponse(request_id="req_001", date="2024-01-01")
        data = resp.model_dump()
        assert data["request_id"] == "req_001"
        assert data["date"] == "2024-01-01"
        assert data["error"] is None

    def test_now_response_json_by_alias(self):
        """测试 NowResponse 通过别名序列化"""
        from api.protoapi_spec.tide_date.v1 import NowResponse

        resp = NowResponse(request_id="req_001", date="2024-01-01")
        data = resp.model_dump(by_alias=True)
        assert data["RequestId"] == "req_001"
        assert data["Date"] == "2024-01-01"


# ========== Domain 层测试 ==========


class TestDomainError:
    """领域错误测试"""

    def test_err_internal(self):
        """测试 ErrInternal 异常"""
        from pkg.tide_date.domain.date.error import ErrInternal

        err = ErrInternal("数据库连接失败")
        assert str(err) == "数据库连接失败"
        assert err.message == "数据库连接失败"

    def test_err_internal_default_message(self):
        """测试 ErrInternal 默认消息"""
        from pkg.tide_date.domain.date.error import ErrInternal

        err = ErrInternal()
        assert str(err) == "Internal error"

    def test_err_internal_is_domain_error(self):
        """测试 ErrInternal 继承自 DateDomainError"""
        from pkg.tide_date.domain.date.error import DateDomainError, ErrInternal

        err = ErrInternal("test")
        assert isinstance(err, DateDomainError)
        assert isinstance(err, Exception)


class TestTideDateEntity:
    """TideDate 实体测试"""

    async def test_now_success(self):
        """测试 now 方法 - 成功"""
        from pkg.tide_date.domain.date.entity import NowRequest, TideDate
        from pkg.tide_date.domain.kit.date import NowResponse as KitNowResponse

        mock_repo = AsyncMock()
        mock_repo.now.return_value = KitNowResponse(date="2024-01-01 12:00:00")

        entity = TideDate(date_repository=mock_repo)
        resp = await entity.now(NowRequest(request_id="req_001"))

        assert resp.date == "2024-01-01 12:00:00"
        mock_repo.now.assert_awaited_once()

    async def test_now_repository_error(self):
        """测试 now 方法 - repository 异常，应抛出 ErrInternal"""
        from pkg.tide_date.domain.date.entity import NowRequest, TideDate
        from pkg.tide_date.domain.date.error import ErrInternal

        mock_repo = AsyncMock()
        mock_repo.now.side_effect = RuntimeError("连接超时")

        entity = TideDate(date_repository=mock_repo)
        with pytest.raises(ErrInternal, match="连接超时"):
            await entity.now(NowRequest(request_id="req_002"))

    async def test_now_error_success(self):
        """测试 now_error 方法 - 成功（正常情况不太可能，但覆盖代码路径）"""
        from pkg.tide_date.domain.date.entity import NowErrorRequest, TideDate
        from pkg.tide_date.domain.kit.date import NowErrorResponse as KitNowErrorResponse

        mock_repo = AsyncMock()
        mock_repo.now_error.return_value = KitNowErrorResponse(date="2024-01-01")

        entity = TideDate(date_repository=mock_repo)
        resp = await entity.now_error(NowErrorRequest(request_id="req_003"))

        assert resp.date == "2024-01-01"
        mock_repo.now_error.assert_awaited_once()

    async def test_now_error_repository_error(self):
        """测试 now_error 方法 - repository 异常"""
        from pkg.tide_date.domain.date.entity import NowErrorRequest, TideDate
        from pkg.tide_date.domain.date.error import ErrInternal

        mock_repo = AsyncMock()
        mock_repo.now_error.side_effect = Exception("Internal")

        entity = TideDate(date_repository=mock_repo)
        with pytest.raises(ErrInternal, match="Internal"):
            await entity.now_error(NowErrorRequest(request_id="req_004"))


class TestDateFactory:
    """DateFactory 工厂测试"""

    def test_create_factory_success(self):
        """测试创建工厂 - 成功"""
        from pkg.tide_date.domain.date.factory import DateFactory, FactoryConfig

        mock_repo = MagicMock()
        config = FactoryConfig(date_repository=mock_repo)
        factory = DateFactory(config)

        assert factory._config.date_repository is mock_repo

    def test_create_factory_missing_repository(self):
        """测试创建工厂 - 缺少 repository"""
        from pkg.tide_date.domain.date.factory import DateFactory, FactoryConfig

        config = FactoryConfig(date_repository=None)
        with pytest.raises(ValueError, match="date_repository is required"):
            DateFactory(config)

    def test_factory_config_validate(self):
        """测试 FactoryConfig.validate - 正常"""
        from pkg.tide_date.domain.date.factory import FactoryConfig

        config = FactoryConfig(date_repository=MagicMock())
        config.validate()  # 不应抛异常

    def test_factory_config_validate_error(self):
        """测试 FactoryConfig.validate - 异常"""
        from pkg.tide_date.domain.date.factory import FactoryConfig

        config = FactoryConfig(date_repository=None)
        with pytest.raises(ValueError):
            config.validate()

    def test_new_tide_date(self):
        """测试工厂创建 TideDate 实体"""
        from pkg.tide_date.domain.date.entity import TideDate
        from pkg.tide_date.domain.date.factory import DateFactory, FactoryConfig

        mock_repo = MagicMock()
        config = FactoryConfig(date_repository=mock_repo)
        factory = DateFactory(config)

        entity = factory.new_tide_date()
        assert isinstance(entity, TideDate)
        assert entity.date_repository is mock_repo

    def test_factory_with_config_funcs(self):
        """测试工厂使用 config_funcs 修改配置"""
        from pkg.tide_date.domain.date.factory import DateFactory, FactoryConfig

        mock_repo = MagicMock()
        config = FactoryConfig(date_repository=None)

        def set_repo(cfg):
            cfg.date_repository = mock_repo

        factory = DateFactory(config, config_funcs=[set_repo])
        assert factory._config.date_repository is mock_repo


# ========== Application 层测试 ==========


class TestApplication:
    """Application 层测试"""

    def test_application_dataclass(self):
        """测试 Application 数据类"""
        from pkg.tide_date.application.application import Application, Commands

        app = Application(commands=Commands(tide_date_handler=MagicMock()))
        assert app.commands is not None
        assert app.commands.tide_date_handler is not None

    def test_application_default(self):
        """测试 Application 默认值"""
        from pkg.tide_date.application.application import Application

        app = Application()
        assert app.commands is None


class TestTideDateHandler:
    """TideDateHandler 测试"""

    async def test_now_success(self):
        """测试 handler.now - 成功"""
        from pkg.tide_date.application.tide_date_handler import TideDateHandler
        from pkg.tide_date.domain.date import NowRequest, NowResponse

        mock_entity = AsyncMock()
        mock_entity.now.return_value = NowResponse(date="2024-01-01 12:00:00")

        mock_factory = MagicMock()
        mock_factory.new_tide_date.return_value = mock_entity

        handler = TideDateHandler(factory=mock_factory)
        resp = await handler.now(NowRequest(request_id="req_001"))

        assert resp.date == "2024-01-01 12:00:00"
        mock_factory.new_tide_date.assert_called_once()
        mock_entity.now.assert_awaited_once()

    async def test_now_error_success(self):
        """测试 handler.now_error - 成功返回"""
        from pkg.tide_date.application.tide_date_handler import TideDateHandler
        from pkg.tide_date.domain.date import NowErrorRequest, NowErrorResponse

        mock_entity = AsyncMock()
        mock_entity.now_error.return_value = NowErrorResponse(date="2024-01-01")

        mock_factory = MagicMock()
        mock_factory.new_tide_date.return_value = mock_entity

        handler = TideDateHandler(factory=mock_factory)
        resp = await handler.now_error(NowErrorRequest(request_id="req_002"))

        assert resp.date == "2024-01-01"

    async def test_now_handler_propagates_exception(self):
        """测试 handler.now - 异常传播"""
        from pkg.tide_date.application.tide_date_handler import TideDateHandler
        from pkg.tide_date.domain.date import NowRequest
        from pkg.tide_date.domain.date.error import ErrInternal

        mock_entity = AsyncMock()
        mock_entity.now.side_effect = ErrInternal("服务不可用")

        mock_factory = MagicMock()
        mock_factory.new_tide_date.return_value = mock_entity

        handler = TideDateHandler(factory=mock_factory)
        with pytest.raises(ErrInternal, match="服务不可用"):
            await handler.now(NowRequest(request_id="req_003"))

    async def test_now_error_handler_propagates_exception(self):
        """测试 handler.now_error - 异常传播"""
        from pkg.tide_date.application.tide_date_handler import TideDateHandler
        from pkg.tide_date.domain.date import NowErrorRequest
        from pkg.tide_date.domain.date.error import ErrInternal

        mock_entity = AsyncMock()
        mock_entity.now_error.side_effect = ErrInternal("Internal")

        mock_factory = MagicMock()
        mock_factory.new_tide_date.return_value = mock_entity

        handler = TideDateHandler(factory=mock_factory)
        with pytest.raises(ErrInternal, match="Internal"):
            await handler.now_error(NowErrorRequest(request_id="req_004"))


# ========== Infrastructure 层测试 ==========


class TestLocalDateRepository:
    """LocalDateRepository 测试"""

    async def test_now_returns_current_time(self):
        """测试 now 返回当前时间"""
        from pkg.tide_date.infrastructure.local.date_repository import (
            LocalDateRepository,
        )
        from pkg.tide_date.domain.kit.date import NowRequest

        repo = LocalDateRepository()
        resp = await repo.now(NowRequest())

        # 验证返回的日期字符串可以被解析
        assert resp.date != ""
        # 验证是合法的 datetime 格式
        parsed = datetime.fromisoformat(resp.date)
        assert parsed.year >= 2024

    async def test_now_error_raises_exception(self):
        """测试 now_error 始终抛出异常"""
        from pkg.tide_date.infrastructure.local.date_repository import (
            LocalDateRepository,
        )
        from pkg.tide_date.domain.kit.date import NowErrorRequest

        repo = LocalDateRepository()
        with pytest.raises(Exception, match="Internal"):
            await repo.now_error(NowErrorRequest(request_id="req_001"))


# ========== Web 层 Controller 测试 ==========


@pytest.fixture
def mock_handler():
    """创建模拟的 tide_date_handler"""
    handler = MagicMock()
    handler.now = AsyncMock()
    handler.now_error = AsyncMock()
    return handler


@pytest.fixture
def mock_app(mock_handler):
    """创建模拟的 Application"""
    from pkg.tide_date.application.application import Application, Commands

    return Application(commands=Commands(tide_date_handler=mock_handler))


@pytest.fixture
def controller(mock_app):
    """创建 DateController 实例"""
    from web.modules.tidedate.controller import DateController

    return DateController(app=mock_app)


class TestControllerError:
    """controller error 模块测试"""

    def test_api_error(self):
        """测试 api_error 转换异常为 Error"""
        from web.modules.tidedate.error import api_error

        err = api_error(RuntimeError("测试错误"))
        assert err.code == 500
        assert err.message == "测试错误"
        assert err.reason == "Internal Server Error"

    def test_api_error_with_domain_error(self):
        """测试 api_error 转换领域异常"""
        from pkg.tide_date.domain.date.error import ErrInternal
        from web.modules.tidedate.error import api_error

        err = api_error(ErrInternal("数据库连接失败"))
        assert err.code == 500
        assert "数据库连接失败" in err.message


class TestDateControllerNow:
    """DateController.now 测试"""

    async def test_now_success(self, controller, mock_handler):
        """测试 now 接口 - 成功"""
        from api.protoapi_spec.tide_date.v1 import NowRequest
        from pkg.tide_date.domain.date import NowResponse as DomainNowResponse

        mock_handler.now.return_value = DomainNowResponse(date="2024-01-01 12:00:00")

        req = NowRequest(request_id="req_001")
        resp = await controller.now(req)

        assert resp.request_id == "req_001"
        assert resp.date == "2024-01-01 12:00:00"
        assert resp.error is None
        mock_handler.now.assert_awaited_once()

    async def test_now_default_request(self, controller, mock_handler):
        """测试 now 接口 - 空请求"""
        from api.protoapi_spec.tide_date.v1 import NowRequest
        from pkg.tide_date.domain.date import NowResponse as DomainNowResponse

        mock_handler.now.return_value = DomainNowResponse(date="2024-01-01")

        req = NowRequest()
        resp = await controller.now(req)

        assert resp.request_id == ""
        assert resp.date == "2024-01-01"

    async def test_now_handler_exception(self, controller, mock_handler):
        """测试 now 接口 - handler 异常，返回 error 而非抛出异常"""
        from api.protoapi_spec.tide_date.v1 import NowRequest

        mock_handler.now.side_effect = RuntimeError("服务崩溃")

        req = NowRequest(request_id="req_err")
        resp = await controller.now(req)

        # controller 捕获异常并返回 error
        assert resp.request_id == "req_err"
        assert resp.error is not None
        assert resp.error.code == 500
        assert "服务崩溃" in resp.error.message

    async def test_now_handler_domain_error(self, controller, mock_handler):
        """测试 now 接口 - 领域层异常"""
        from api.protoapi_spec.tide_date.v1 import NowRequest
        from pkg.tide_date.domain.date.error import ErrInternal

        mock_handler.now.side_effect = ErrInternal("数据库错误")

        req = NowRequest(request_id="req_domain_err")
        resp = await controller.now(req)

        assert resp.error is not None
        assert resp.error.code == 500
        assert "数据库错误" in resp.error.message


class TestDateControllerNowError:
    """DateController.now_error 测试"""

    async def test_now_error_success(self, controller, mock_handler):
        """测试 now_error 接口 - 成功"""
        from api.protoapi_spec.tide_date.v1 import NowErrorRequest
        from pkg.tide_date.domain.date import NowErrorResponse as DomainNowErrorResponse

        mock_handler.now_error.return_value = DomainNowErrorResponse(
            date="2024-01-01 12:00:00"
        )

        req = NowErrorRequest(request_id="req_001")
        resp = await controller.now_error(req)

        assert resp.request_id == "req_001"
        assert resp.date == "2024-01-01 12:00:00"
        assert resp.error is None
        mock_handler.now_error.assert_awaited_once()

    async def test_now_error_handler_exception(self, controller, mock_handler):
        """测试 now_error 接口 - handler 异常"""
        from api.protoapi_spec.tide_date.v1 import NowErrorRequest

        mock_handler.now_error.side_effect = Exception("Internal")

        req = NowErrorRequest(request_id="req_err")
        resp = await controller.now_error(req)

        assert resp.error is not None
        assert resp.error.code == 500
        assert "Internal" in resp.error.message


# ========== 路由注册测试 ==========


class TestDateControllerRoutes:
    """DateController 路由注册测试"""

    def test_register_routes_with_app(self, controller):
        """测试路由注册 - web_server 有 app 属性"""
        mock_web_server = MagicMock()
        mock_fastapi_app = MagicMock()
        mock_web_server.app = mock_fastapi_app

        controller.register_routes(mock_web_server)

        # 验证 GET+POST /Now 和 GET+POST /NowError 路由注册
        get_calls = mock_fastapi_app.get.call_args_list
        post_calls = mock_fastapi_app.post.call_args_list

        get_paths = [call.args[0] for call in get_calls]
        post_paths = [call.args[0] for call in post_calls]

        assert "/Now" in get_paths
        assert "/NowError" in get_paths
        assert "/Now" in post_paths
        assert "/NowError" in post_paths

    def test_register_routes_with_router(self, controller):
        """测试路由注册 - web_server 有 router 属性"""
        mock_web_server = MagicMock(spec=[])
        mock_web_server.app = None
        mock_router = MagicMock()
        mock_web_server.router = mock_router

        controller.register_routes(mock_web_server)

        # 验证路由注册到了 router 上
        assert mock_router.get.called
        assert mock_router.post.called

    def test_register_routes_no_app_or_router(self, controller):
        """测试路由注册 - 无 app 也无 router"""
        mock_web_server = MagicMock(spec=[])
        mock_web_server.app = None
        mock_web_server.router = None

        with pytest.raises(
            AttributeError, match="web_server must have 'app' or 'router' attribute"
        ):
            controller.register_routes(mock_web_server)


# ========== Plugin 层测试 ==========


def _load_plugin_web_handler():
    """通过 importlib 从文件路径加载 plugin_web_handler 模块。

    因为 cmd 目录名与 Python 标准库 cmd 模块冲突，
    且 tide-date 包含连字符不能直接 import。
    """
    import importlib.util
    import os

    module_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "cmd",
        "tide-date",
        "app",
        "options",
        "plugin_web_handler.py",
    )
    module_path = os.path.abspath(module_path)
    spec = importlib.util.spec_from_file_location("plugin_web_handler", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestInstallWebHandler:
    """install_web_handler 插件测试"""

    def test_install_success(self):
        """测试成功安装 web handler"""
        module = _load_plugin_web_handler()
        install_web_handler = module.install_web_handler

        mock_web_server = MagicMock()
        mock_fastapi_app = MagicMock()
        mock_web_server.app = mock_fastapi_app

        # 应该不抛异常
        install_web_handler(mock_web_server)

        # 验证路由已注册（GET+POST /Now、GET+POST /NowError）
        assert mock_fastapi_app.get.called
        assert mock_fastapi_app.post.called

    def test_install_registers_correct_routes(self):
        """测试安装后路由路径正确"""
        module = _load_plugin_web_handler()
        install_web_handler = module.install_web_handler

        mock_web_server = MagicMock()
        mock_fastapi_app = MagicMock()
        mock_web_server.app = mock_fastapi_app

        install_web_handler(mock_web_server)

        get_paths = [call.args[0] for call in mock_fastapi_app.get.call_args_list]
        post_paths = [call.args[0] for call in mock_fastapi_app.post.call_args_list]

        assert "/Now" in get_paths
        assert "/NowError" in get_paths
        assert "/Now" in post_paths
        assert "/NowError" in post_paths
