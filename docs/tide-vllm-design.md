# Tide-VLLM 模块设计文档

## 1. 模块简介

`tide-vllm` 是 Tide 框架中的一个模板示例模块，主要演示如何集成 vLLM 推理引擎来提供大语言模型（LLM）服务。该模块支持：

- **自动启动模式**：在服务启动时自动启动 vLLM server 并加载模型
- **手动连接模式**：连接到已运行的外部 vLLM server

默认配置使用**千问3（Qwen2.5-7B-Instruct）**模型作为示例。

## 2. 架构设计

### 2.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                      tide-vllm 服务                           │
│  ┌─────────────────┐    ┌─────────────────────────────────┐  │
│  │ Web Server      │    │ VLLMServerManager               │  │
│  │ (port 10002)    │    │ (启动/停止/监控 vLLM 进程)       │  │
│  └────────┬────────┘    └──────────────┬──────────────────┘  │
│           │                            │                      │
│           │      ┌─────────────────────▼───────────────┐     │
│           │      │ vLLM Server Process                 │     │
│           │      │ (subprocess, port 8000)             │     │
│           │      │ 加载模型: Qwen/Qwen2.5-7B-Instruct   │     │
│           │      └─────────────────────────────────────┘     │
│           │                            │                      │
│           └──────────► VLLMClient ─────┘                      │
│                    (HTTP /v1/chat/completions)                │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 DDD 分层架构

模块采用领域驱动设计（DDD）架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Layer                             │
│                    (ChatController)                          │
│                 处理 HTTP 请求/响应                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Application Layer                         │
│                     (ChatHandler)                            │
│                   处理业务用例逻辑                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Domain Layer                            │
│         (ChatEntity, ChatFactory, ChatRepository)            │
│                   定义领域模型和接口                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Infrastructure Layer                        │
│             (VLLMClient, VLLMChatRepository)                 │
│              实现与 vLLM 服务器的通信                         │
└─────────────────────────────────────────────────────────────┘
```

## 3. 目录结构

```
tide/
├── cmd/tide-vllm/                    # 命令入口
│   ├── __init__.py
│   ├── main.py                       # 服务入口
│   └── app/
│       ├── __init__.py
│       ├── server.py                 # 服务器启动逻辑
│       └── options/
│           ├── __init__.py
│           ├── options.py            # 配置选项（VLLMConfig）
│           ├── plugin_logs.py        # 日志插件
│           ├── plugin_config.py      # 配置插件
│           ├── plugin_vllm.py        # vLLM 服务管理器
│           └── plugin_web_handler.py # Web 处理器插件
│
├── pkg/tide_vllm/                    # 业务逻辑包（DDD架构）
│   ├── __init__.py
│   ├── provider/                     # 全局服务提供者
│   │   ├── __init__.py
│   │   └── provider.py
│   ├── domain/                       # 领域层
│   │   ├── __init__.py
│   │   └── chat/
│   │       ├── __init__.py
│   │       ├── entity.py             # 聊天实体和值对象
│   │       ├── repository.py         # 仓库接口
│   │       └── factory.py            # 工厂
│   ├── application/                  # 应用层
│   │   ├── __init__.py
│   │   ├── application.py            # 应用定义
│   │   └── chat_handler.py           # 聊天处理器
│   └── infrastructure/               # 基础设施层
│       ├── __init__.py
│       └── vllm/
│           ├── __init__.py
│           ├── vllm_client.py        # vLLM HTTP 客户端
│           └── vllm_repository.py    # vLLM 仓库实现
│
├── web/modules/tidevllm/             # Web 控制器
│   ├── __init__.py
│   └── controller.py                 # HTTP 路由控制器
│
└── conf/tide-vllm.yaml               # 配置文件
```

## 4. 核心组件

### 4.1 VLLMServerManager

位于 `cmd/tide-vllm/app/options/plugin_vllm.py`，负责管理 vLLM server 进程的生命周期：

- **启动 vLLM server**：使用 `subprocess.Popen` 启动 vLLM 进程
- **等待就绪**：通过 `/v1/models` 端点检查模型是否加载完成
- **健康检查**：监控 vLLM server 进程状态
- **优雅停止**：使用 SIGTERM → SIGKILL 进行进程清理
- **日志记录**：异步记录 vLLM 输出日志

### 4.2 VLLMClient

位于 `pkg/tide_vllm/infrastructure/vllm/vllm_client.py`，实现与 vLLM server 的 HTTP 通信：

- 使用 `httpx` 库进行异步 HTTP 请求
- 支持 OpenAI 兼容的 `/v1/chat/completions` 接口
- 提供健康检查和模型列表查询功能

### 4.3 ChatHandler

位于 `pkg/tide_vllm/application/chat_handler.py`，处理聊天相关的业务逻辑：

- 接收用户请求，构建消息列表
- 调用领域服务进行 LLM 推理
- 返回格式化的响应结果

## 5. 配置说明

配置文件位于 `conf/tide-vllm.yaml`：

```yaml
# Web 服务配置
web:
  bind_address:
    host: "0.0.0.0"
    port: 10002          # tide-vllm 服务端口

# vLLM 配置
vllm:
  enabled: true          # 是否启用 vLLM
  
  # 启动模式
  auto_start: true       # true: 自动启动 vLLM server
                         # false: 连接外部 vLLM server
  
  # vLLM 服务器地址
  host: "0.0.0.0"
  port: 8000             # vLLM server 端口
  
  # 模型配置
  model_name: "Qwen2.5-7B-Instruct"           # served model name
  model_path: "Qwen/Qwen2.5-7B-Instruct"      # 模型路径/HuggingFace ID
  
  # 生成参数
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9
  timeout: 60            # 请求超时（秒）
  
  # vLLM Server 启动参数（仅 auto_start=true 时有效）
  gpu_memory_utilization: 0.9    # GPU 显存使用率
  tensor_parallel_size: 1        # 张量并行大小
  max_num_seqs: 256              # 最大并发序列数
  max_num_batched_tokens: 8192   # 最大批处理 token 数
  max_model_len: 4096            # 模型最大上下文长度
  dtype: "auto"                  # 数据类型
  startup_timeout: 600           # 启动超时时间（秒）
  enable_prefix_caching: true    # 启用前缀缓存
  enable_chunked_prefill: true   # 启用分块预填充
```

## 6. API 接口

### 6.1 健康检查

```bash
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "vllm_healthy": true
}
```

### 6.2 聊天补全

```bash
POST /chat/completions
POST /v1/chat/completions    # OpenAI 兼容路径
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `prompt` | string | ✅ | 用户输入的提示词 |
| `system_prompt` | string | ❌ | 系统提示词（默认："你是一个有用的AI助手。"） |
| `request_id` | string | ❌ | 请求ID（不填自动生成 UUID） |
| `max_tokens` | int | ❌ | 最大生成 token 数 |
| `temperature` | float | ❌ | 温度参数（控制随机性） |
| `top_p` | float | ❌ | top_p 参数 |

**请求示例：**

```bash
curl -X POST http://localhost:10002/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "你好，请介绍一下你自己",
    "system_prompt": "你是一个友好的AI助手",
    "max_tokens": 512
  }'
```

**响应示例：**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "你好！我是一个AI助手，由人工智能技术驱动...",
  "model": "Qwen2.5-7B-Instruct",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 150,
    "total_tokens": 170
  },
  "finish_reason": "stop",
  "error": null
}
```

## 7. 使用指南

### 7.1 方式一：自动启动模式（推荐）

配置 `auto_start: true`，服务启动时自动启动 vLLM server。

**前提条件：**
- 安装 vLLM：`pip install vllm`
- 有可用的 GPU 和足够的显存

**启动服务：**
```bash
cd tide
python cmd/tide-vllm/main.py -c conf/tide-vllm.yaml
```

### 7.2 方式二：手动连接模式

配置 `auto_start: false`，需要先手动启动 vLLM server。

**步骤 1：启动 vLLM server**
```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8000 \
  --served-model-name Qwen2.5-7B-Instruct
```

或使用 Python 命令：
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

**步骤 2：启动 tide-vllm 服务**
```bash
python cmd/tide-vllm/main.py -c conf/tide-vllm.yaml
```

### 7.3 测试服务

```bash
# 健康检查
curl http://localhost:10002/health

# 聊天请求
curl -X POST http://localhost:10002/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "什么是机器学习？",
    "system_prompt": "你是一个专业的AI技术专家",
    "max_tokens": 1024
  }'
```

## 8. 常见问题

### 8.1 vLLM 能否在 Mac 上运行？

**不能直接运行。** vLLM 目前仅支持 CUDA（NVIDIA GPU），Mac 系统不满足运行条件：

- Mac（Intel）：无 NVIDIA GPU
- Mac（Apple Silicon）：使用 Metal，不支持 CUDA

**替代方案：**
1. 使用 [Ollama](https://ollama.ai/) - 支持 Mac 的本地 LLM 推理
2. 使用云端 GPU 服务器运行 vLLM
3. 使用 vLLM 的 CPU 模式（性能较差）

### 8.2 启动时报错 "vLLM 命令未找到"

确保已安装 vLLM：
```bash
pip install vllm
```

或者设置 `auto_start: false`，手动启动 vLLM server。

### 8.3 模型加载超时

模型首次加载需要下载，可能需要较长时间。可以调整配置：
```yaml
vllm:
  startup_timeout: 1200  # 增加超时时间到 20 分钟
```

### 8.4 显存不足

可以调整以下参数：
```yaml
vllm:
  gpu_memory_utilization: 0.8  # 降低显存使用率
  max_model_len: 2048          # 减少上下文长度
```

或使用更小的模型：
```yaml
vllm:
  model_path: "Qwen/Qwen2.5-3B-Instruct"  # 使用 3B 版本
```

## 9. 技术选型说明

### 9.1 HTTP 客户端：httpx vs aiohttp

本模块选用 **httpx** 作为 HTTP 客户端：

| 特性 | httpx | aiohttp |
|------|-------|---------|
| API 风格 | 类 requests，更直观 | 传统 aiohttp 风格 |
| 同步/异步 | 同时支持 | 仅支持异步 |
| HTTP/2 | ✅ 支持 | ❌ 不支持 |
| 学习成本 | 低（与 requests 一致） | 较高 |

### 9.2 为什么选择 vLLM？

- **高性能**：PagedAttention 技术，显存利用率高
- **兼容性好**：OpenAI API 兼容，易于集成
- **生产就绪**：支持连续批处理、动态调度

## 10. 参考资料

- [vLLM 官方文档](https://docs.vllm.ai/)
- [Qwen2.5 模型](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [httpx 文档](https://www.python-httpx.org/)
