# -*- coding: utf-8 -*-
"""vLLM Chat Repository - vLLM 聊天仓库实现

实现 ChatRepository 接口，使用 vLLM 客户端与服务交互
"""

import logging
from typing import Optional

from pkg.tide_vllm.domain.chat import ChatRepository, ChatRequest, ChatResponse
from pkg.tide_vllm.provider import global_provider

logger = logging.getLogger(__name__)


class VLLMChatRepository(ChatRepository):
    """vLLM 聊天仓库实现
    
    使用 vLLM 客户端实现聊天功能
    """
    
    def __init__(self):
        """初始化仓库"""
        pass
    
    def _get_client(self):
        """获取 vLLM 客户端
        
        从全局 provider 获取客户端实例
        """
        provider = global_provider()
        if provider.vllm_client is None:
            raise RuntimeError("vLLM 客户端未初始化，请检查配置")
        return provider.vllm_client
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """发送聊天请求
        
        Args:
            request: 聊天请求
            
        Returns:
            ChatResponse: 聊天响应
        """
        client = self._get_client()
        
        # 转换消息格式
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.messages
        ]
        
        logger.info(f"处理聊天请求: request_id={request.request_id}")
        
        try:
            # 调用 vLLM API
            result = await client.chat_completion(
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            )
            
            # 解析响应
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            finish_reason = choice.get("finish_reason", "")
            
            usage = result.get("usage", {})
            model = result.get("model", "")
            
            response = ChatResponse(
                request_id=request.request_id,
                content=content,
                model=model,
                usage=usage,
                finish_reason=finish_reason,
            )
            
            logger.info(
                f"聊天请求完成: request_id={request.request_id}, "
                f"tokens={usage.get('total_tokens', 0)}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"聊天请求失败: request_id={request.request_id}, error={e}")
            raise
    
    async def health_check(self) -> bool:
        """健康检查
        
        检查 vLLM 服务是否健康。
        如果使用了 auto_start，还会检查 vLLM server 进程状态。
        
        Returns:
            bool: 服务是否健康
        """
        try:
            provider = global_provider()
            
            # 如果有 vLLM server manager（auto_start 模式），检查其状态
            if provider.vllm_server_manager:
                server_healthy = await provider.vllm_server_manager.health_check()
                if not server_healthy:
                    logger.warning("vLLM server 进程健康检查失败")
                    return False
            
            # 检查客户端连接
            client = self._get_client()
            return await client.health_check()
        except Exception as e:
            logger.warning(f"健康检查失败: {e}")
            return False
