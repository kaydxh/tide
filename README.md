
# Tide

**Tide** 是一个基于 Python 的 Web/gRPC 微服务框架，参考 Go 版本 **Sea 框架** 的架构设计，底层依赖 **Peek** 基础库，采用 **领域驱动设计（DDD）** + **Clean Architecture** 分层架构。

## ✨ 核心特性

- **HTTP + gRPC 双协议支持**：基于 FastAPI 提供 HTTP 服务，同时支持 gRPC 服务
- **DDD 分层架构**：业务模块统一遵循 Domain → Application → Infrastructure 分层设计
- **插件机制**：通过 Plugin 灵活扩展框架能力（日志、监控、数据库、OpenTelemetry 等）
- **依赖注入**：通过 Provider 模式管理全局依赖，降低模块间耦合
- **Proto 驱动的 API 定义**：使用 Protobuf 定义 API，同时生成 gRPC 和 HTTP 接口
- **可观测性**：内置 OpenTelemetry 链路追踪、指标上报、日志管理
- **进程资源监控**：内置 CPU/内存/GPU 监控与 Debug API
- **QPS 限流**：支持 HTTP 和 gRPC 层面的 QPS 限流与并发控制

## 📁 项目结构

```
tide/
├── src/tide/                  # 框架核心层（与业务无关）
│   ├── app/                   #   TideApp、Command、Plugin
│   ├── config/                #   配置管理（TideConfig、WebConfig 等）
│   └── provider/              #   全局依赖注入容器（单例模式）
│
├── pkg/                       # 业务逻辑层（DDD 分层架构）
│   ├── tide_date/             #   日期服务（框架示例模块）
│   ├── tide_vllm/             #   vLLM 推理服务
│   └── tide_vllm_wxvideo.../  #   微信视频场景审核服务
│
├── cmd/                       # 各业务服务的启动入口
│   ├── tide-date/             #   日期服务入口
│   ├── tide-vllm/             #   vLLM 推理服务入口
│   └── tide-vllm-wxvideo.../  #   微信视频场景审核服务入口
│
├── web/                       # Web 层（Controller / 路由注册）
│   └── modules/
│       └── tidedate/          #   日期服务的 HTTP/gRPC Controller
│
├── api/                       # API 定义（Protobuf）
│   └── protoapi_spec/
│       └── tide_date/v1/      #   日期服务 proto 定义 + 自动生成的 schemas.py
│
├── conf/                      # 配置文件
├── docker/                    # Docker 构建文件
├── docs/                      # 设计文档
├── scripts/                   # 脚本工具
├── tests/                     # 单元测试
├── Makefile                   # 构建 & 工具命令
└── pyproject.toml             # 项目元信息 & 依赖
```

**每个业务模块（`pkg/tide_xxx/`）** 遵循 DDD 分层：

```
pkg/tide_xxx/
├── application/           # 应用层 — 用例编排（Handler）
├── domain/                # 领域层 — 实体、接口、工厂、异常
│   └── xxx/
│       ├── entity.py          # 领域实体和值对象
│       ├── repository.py      # Repository 抽象接口（ABC）
│       ├── factory.py         # 工厂方法
│       └── error.py           # 领域异常
└── infrastructure/        # 基础设施层 — Repository 具体实现
```

## 🚀 快速上手

### 环境要求

- Python >= 3.9
- [Peek](https://github.com/kaydxh/peek) 基础库（可选，如需本地开发调试 peek 则需额外安装）

### 方式一：使用开发脚本安装

如果需要同时开发调试 peek 基础库，可使用开发脚本一键安装：

```bash
# 需要 peek 库与 tide 在同级目录
# ├── peek/
# └── tide/

cd tide
./scripts/dev_install.sh
```

该脚本会自动：创建虚拟环境 → 安装本地 peek（editable 模式）→ 安装 tide 及全部依赖。

### 方式二：手动安装（推荐）

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装 tide（含所有可选依赖）
pip install -e ".[all]"

# 3.（可选）如需本地调试 peek，以 editable 模式安装
# pip install -e ../peek
```

### 启动服务

以示例服务 `tide-date` 为例：

```bash
# 使用默认配置启动
python ./cmd/tide-date/main.py --config ./conf/tide-date.yaml
```

启动成功后可以看到类似日志：

```
[INFO] 日志初始化完成: level=info, formatter=glog, redirect=both, filepath=./log
[INFO] 配置已安装: ['log', 'web', 'database', 'monitor']
[INFO] gRPC default interceptor chain installed: 5 interceptors
[INFO] WebServer created: http://0.0.0.0:10001
[INFO] gRPC server started on 0.0.0.0:10002
INFO:  Uvicorn running on http://0.0.0.0:10001 (Press CTRL+C to quit)
```

服务启动后会同时监听：
- **HTTP**: `http://0.0.0.0:10001`
- **gRPC**: `0.0.0.0:10002`

## 🔍 调试示例

### 1. HTTP 接口调用

```bash
# 调用 Now 接口获取当前时间
curl -X POST http://localhost:10001/Now

# 返回示例
# {"RequestId": "", "Date": "2026-02-24 15:00:00.123456", "Error": null}
```

### 2. gRPC 接口调用

使用 `grpcurl` 工具进行调试：

```bash
# 列出可用服务
grpcurl -plaintext localhost:10002 list

# 调用 Now 方法
grpcurl -plaintext -d '{"request_id": "test-001"}' \
  localhost:10002 tide.api.tidedate.TideDateService/Now
```

### 3. 进程资源监控 API

服务启动后会自动注册监控 Debug 端点：

```bash
# 获取当前进程资源快照（CPU、内存等）
curl http://localhost:10001/debug/monitor/snapshot

# 获取资源使用摘要（历史统计）
curl http://localhost:10001/debug/monitor/summary

# 手动启动/停止持续采集
curl -X POST http://localhost:10001/debug/monitor/start
curl -X POST http://localhost:10001/debug/monitor/stop

# 获取监控报告
curl http://localhost:10001/debug/monitor/report
```

### 4. 运行单元测试

```bash
# 运行所有测试（含覆盖率）
make test

# 或直接使用 pytest
pytest tests/ -v
```

### 5. Proto 编译

当修改了 `api/protoapi_spec/` 下的 `.proto` 文件后，需要重新编译：

```bash
# 检查 proto 编译工具是否安装
make proto-check

# 编译所有 proto 文件（含 gRPC 代码 + Pydantic schemas）
make proto

# 编译单个服务的 proto
make proto-service SERVICE=tide_date/v1

# 仅重新生成 Pydantic schemas（不重新编译 proto）
make proto-models

# 列出所有 proto 文件
make proto-list

# 清理生成的 proto 文件（schemas.py 和 __init__.py 不会被清理）
make proto-clean
```

`make proto` 执行时会自动：
1. 调用 `protoc` 编译 `.proto` 文件，生成 `*_pb2.py`、`*_pb2.pyi`、`*_pb2_grpc.py`
2. 调用 `scripts/gen_pydantic_models.py` 从 proto 定义生成 `schemas.py`（Pydantic 模型）和 `__init__.py`

## ⚙️ 配置说明

配置文件位于 `conf/` 目录，采用 YAML 格式，主要包含以下模块：

| 配置模块 | 说明 |
|---|---|
| `log` | 日志配置：级别、格式、输出方式（stdout/file/both）、轮转策略 |
| `web` | Web 服务配置：监听地址、gRPC 开关、OpenTelemetry、QPS 限流 |
| `database` | 数据库配置：MySQL、Redis 连接参数 |
| `monitor` | 进程资源监控：采集间隔、GPU 监控、历史记录 |
| `vllm` | vLLM 推理配置（仅 vLLM 相关服务）：模型路径、GPU 参数、视频解码等 |

配置示例参见 [conf/tide-date.yaml](conf/tide-date.yaml)。

## 📦 Makefile 常用命令

```bash
make build          # 构建项目（pip install -e .）
make install        # 安装全部依赖
make install-dev    # 安装开发依赖
make test           # 运行测试（含覆盖率）
make lint           # 代码检查（flake8 + mypy + black + isort）
make format         # 代码格式化
make clean          # 清理构建产物
make proto          # 编译所有 proto 文件（含 Pydantic schemas 生成）
make proto-service  # 编译单个服务 proto（SERVICE=tide_date/v1）
make proto-models   # 仅生成 Pydantic schemas（不编译 proto）
make proto-clean    # 清理生成的 proto 文件
make proto-list     # 列出所有 proto 文件
make proto-check    # 检查 proto 编译工具
make help           # 查看所有可用命令
```

## 📄 License

MIT License