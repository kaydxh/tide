#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin: Web Handler - Similar to sea's plugin.web_handler.go

This is where we wire up the DDD layers:
- Domain (Entity, Repository, Factory)
- Application (Handlers/Use Cases)
- Infrastructure (Repository implementations)
- Web (Controllers/Routes)
"""

import logging

logger = logging.getLogger(__name__)


def install_web_handler(web_server):
    """Install web handlers.

    Similar to sea's installWebHandlerOrDie.

    This function wires up the DDD layers:
    1. Create Domain Factory with Infrastructure Repository
    2. Create Application with Commands/Handlers
    3. Create Web Controller with Application
    4. Register routes to WebServer
    """
    try:
        # Import DDD layers
        from pkg.tide_date.domain.date import DateFactory, FactoryConfig
        from pkg.tide_date.infrastructure.local import LocalDateRepository
        from pkg.tide_date.application import Application, Commands, TideDateHandler
        from web.modules.tidedate.controller import DateController

        # 1. Create Domain Factory with Infrastructure Repository
        factory_config = FactoryConfig(
            date_repository=LocalDateRepository()
        )
        date_factory = DateFactory(factory_config)

        # 2. Create Application with Commands/Handlers
        app = Application(
            commands=Commands(
                tide_date_handler=TideDateHandler(date_factory)
            )
        )

        # 3. Create Controller with Application
        controller = DateController(app)

        # 4. Register routes to WebServer
        controller.register_routes(web_server)

        logger.info("Web handlers installed successfully")

    except ImportError as e:
        logger.error(f"Failed to import DDD modules: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to install web handlers: {e}")
        raise
