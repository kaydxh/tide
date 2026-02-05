#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Web Handler - Web 处理器插件

该模块负责设置 DDD 层：
- Domain（实体、仓库、工厂）
- Application（处理器/用例）
- Infrastructure（仓库实现）
- Web（控制器/路由）
"""

import logging

logger = logging.getLogger(__name__)


def install_web_handler(web_server):
    """安装 Web 处理器。

    该函数设置 DDD 层：
    1. 创建带有基础设施仓库的领域工厂
    2. 创建带有命令/处理器的应用
    3. 创建带有应用的 Web 控制器
    4. 将路由注册到 WebServer
    """
    try:
        # 导入 DDD 层
        from pkg.tide_vllm.domain.chat import ChatFactory, FactoryConfig
        from pkg.tide_vllm.infrastructure.vllm import VLLMChatRepository
        from pkg.tide_vllm.application import Application, Commands, ChatHandler
        from web.modules.tidevllm.controller import ChatController

        # 1. 创建带有基础设施仓库的领域工厂
        factory_config = FactoryConfig(
            chat_repository=VLLMChatRepository()
        )
        chat_factory = ChatFactory(factory_config)

        # 2. 创建带有命令/处理器的应用
        app = Application(
            commands=Commands(
                chat_handler=ChatHandler(chat_factory)
            )
        )

        # 3. 创建带有应用的控制器
        controller = ChatController(app)

        # 4. 将路由注册到 WebServer
        controller.register_routes(web_server)

        logger.info("Web 处理器安装成功")

    except ImportError as e:
        logger.error(f"导入 DDD 模块失败: {e}")
        raise
    except Exception as e:
        logger.error(f"安装 Web 处理器失败: {e}")
        raise
