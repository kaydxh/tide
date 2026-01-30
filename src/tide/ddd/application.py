#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application - 应用层基类

参考 Go 版本 sea 的 application/application.go 实现
提供命令和查询处理的基础架构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel


# 命令和查询的结果类型
R = TypeVar("R")


class Command(BaseModel):
    """
    命令基类

    命令表示一个会改变系统状态的操作
    """

    pass


class Query(BaseModel):
    """
    查询基类

    查询表示一个不会改变系统状态的操作
    """

    pass


class CommandHandler(ABC, Generic[R]):
    """
    命令处理器基类

    处理特定类型的命令

    使用示例：
        class CreateUserHandler(CommandHandler[User]):
            def __init__(self, user_factory: UserFactory):
                self.user_factory = user_factory

            def handle(self, cmd: CreateUserCommand) -> User:
                return self.user_factory.create(**cmd.model_dump())
    """

    @abstractmethod
    def handle(self, command: Command) -> R:
        """
        处理命令

        Args:
            command: 命令对象

        Returns:
            处理结果
        """
        pass


class AsyncCommandHandler(ABC, Generic[R]):
    """异步命令处理器基类"""

    @abstractmethod
    async def handle(self, command: Command) -> R:
        """异步处理命令"""
        pass


class QueryHandler(ABC, Generic[R]):
    """
    查询处理器基类

    处理特定类型的查询
    """

    @abstractmethod
    def handle(self, query: Query) -> R:
        """
        处理查询

        Args:
            query: 查询对象

        Returns:
            查询结果
        """
        pass


class AsyncQueryHandler(ABC, Generic[R]):
    """异步查询处理器基类"""

    @abstractmethod
    async def handle(self, query: Query) -> R:
        """异步处理查询"""
        pass


@dataclass
class Commands:
    """
    命令集合

    存储应用的所有命令处理器
    """

    handlers: Dict[str, CommandHandler] = field(default_factory=dict)

    def register(self, name: str, handler: CommandHandler) -> "Commands":
        """注册命令处理器"""
        self.handlers[name] = handler
        return self

    def get(self, name: str) -> Optional[CommandHandler]:
        """获取命令处理器"""
        return self.handlers.get(name)


@dataclass
class Queries:
    """
    查询集合

    存储应用的所有查询处理器
    """

    handlers: Dict[str, QueryHandler] = field(default_factory=dict)

    def register(self, name: str, handler: QueryHandler) -> "Queries":
        """注册查询处理器"""
        self.handlers[name] = handler
        return self

    def get(self, name: str) -> Optional[QueryHandler]:
        """获取查询处理器"""
        return self.handlers.get(name)


@dataclass
class Application:
    """
    应用层

    组织命令和查询处理器

    使用示例：
        app = Application(
            commands=Commands(handlers={
                "create_user": CreateUserHandler(user_factory),
            }),
            queries=Queries(handlers={
                "get_user": GetUserHandler(user_repo),
            }),
        )

        # 执行命令
        user = app.commands.get("create_user").handle(CreateUserCommand(...))

        # 执行查询
        user = app.queries.get("get_user").handle(GetUserQuery(id=1))
    """

    commands: Commands = field(default_factory=Commands)
    queries: Queries = field(default_factory=Queries)

    def execute_command(self, name: str, command: Command) -> Any:
        """
        执行命令

        Args:
            name: 命令处理器名称
            command: 命令对象

        Returns:
            执行结果

        Raises:
            ValueError: 如果命令处理器不存在
        """
        handler = self.commands.get(name)
        if not handler:
            raise ValueError(f"Command handler '{name}' not found")
        return handler.handle(command)

    def execute_query(self, name: str, query: Query) -> Any:
        """
        执行查询

        Args:
            name: 查询处理器名称
            query: 查询对象

        Returns:
            查询结果

        Raises:
            ValueError: 如果查询处理器不存在
        """
        handler = self.queries.get(name)
        if not handler:
            raise ValueError(f"Query handler '{name}' not found")
        return handler.handle(query)
