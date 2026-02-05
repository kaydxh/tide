# -*- coding: utf-8 -*-
"""Chat Controller - 聊天控制器

处理 HTTP 请求，调用应用层处理器
"""

import logging
import uuid
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pkg.tide_vllm.application import Application

logger = logging.getLogger(__name__)


# ========== 请求/响应模型 ==========

class ChatCompletionRequest(BaseModel):
    """聊天补全请求"""
    request_id: Optional[str] = Field(default=None, description="请求ID")
    prompt: str = Field(..., description="用户输入的提示词")
    system_prompt: Optional[str] = Field(
        default="你是一个有用的AI助手。",
        description="系统提示词"
    )
    max_tokens: Optional[int] = Field(default=None, description="最大生成token数")
    temperature: Optional[float] = Field(default=None, description="温度参数")
    top_p: Optional[float] = Field(default=None, description="top_p参数")


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""
    request_id: str = Field(..., description="请求ID")
    content: str = Field(..., description="生成的内容")
    model: str = Field(default="", description="使用的模型")
    usage: dict = Field(default_factory=dict, description="token使用情况")
    finish_reason: str = Field(default="", description="完成原因")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    vllm_healthy: bool = Field(..., description="vLLM服务是否健康")


# ========== 控制器 ==========

class ChatController:
    """聊天控制器
    
    处理聊天相关的 HTTP 请求
    """
    
    def __init__(self, app: "Application"):
        """初始化控制器
        
        Args:
            app: 应用层实例
        """
        self._app = app
    
    def register_routes(self, web_server):
        """注册路由到 Web 服务器
        
        Args:
            web_server: GenericWebServer 或 FallbackWebServer 实例
        """
        # 获取 FastAPI app
        app = getattr(web_server, 'app', None)
        if app is None:
            router = getattr(web_server, 'router', None)
            if router is None:
                raise AttributeError("web_server 必须有 'app' 或 'router' 属性")
            app = router
        
        @app.get("/health")
        async def health():
            """健康检查端点
            
            curl http://localhost:10002/health
            """
            return await self.health()
        
        @app.post("/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """聊天补全端点
            
            使用千问3模型进行对话
            
            curl -X POST http://localhost:10002/chat/completions \
              -H "Content-Type: application/json" \
              -d '{
                "prompt": "你好，请介绍一下你自己",
                "system_prompt": "你是一个友好的AI助手",
                "max_tokens": 512
              }'
            """
            return await self.chat_completions(request)
        
        @app.post("/v1/chat/completions")
        async def v1_chat_completions(request: ChatCompletionRequest):
            """OpenAI 兼容的聊天补全端点
            
            与 /chat/completions 功能相同，提供 OpenAI 兼容的路径
            """
            return await self.chat_completions(request)
    
    async def health(self) -> HealthResponse:
        """健康检查
        
        Returns:
            HealthResponse: 健康检查响应
        """
        try:
            vllm_healthy = await self._app.commands.chat_handler.health_check()
            return HealthResponse(
                status="healthy" if vllm_healthy else "degraded",
                vllm_healthy=vllm_healthy,
            )
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return HealthResponse(
                status="unhealthy",
                vllm_healthy=False,
            )
    
    async def chat_completions(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """处理聊天补全请求
        
        Args:
            request: 聊天补全请求
            
        Returns:
            ChatCompletionResponse: 聊天补全响应
        """
        # 生成请求ID
        request_id = request.request_id or str(uuid.uuid4())
        
        try:
            from pkg.tide_vllm.application.chat_handler import (
                ChatCompletionRequest as DomainRequest,
            )
            
            # 转换为领域请求
            domain_request = DomainRequest(
                request_id=request_id,
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            )
            
            # 调用处理器
            domain_response = await self._app.commands.chat_handler.chat_completion(
                domain_request
            )
            
            return ChatCompletionResponse(
                request_id=domain_response.request_id,
                content=domain_response.content,
                model=domain_response.model,
                usage=domain_response.usage or {},
                finish_reason=domain_response.finish_reason,
            )
            
        except Exception as e:
            logger.error(f"聊天补全请求失败: request_id={request_id}, error={e}")
            return ChatCompletionResponse(
                request_id=request_id,
                content="",
                error=str(e),
            )
