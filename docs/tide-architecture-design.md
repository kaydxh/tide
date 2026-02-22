# Tide 框架架构设计文档

## 1. 设计理念

Tide 是一个 Python Web/gRPC 服务框架，参考了 Go 版本 **Sea 框架**的架构设计思想。核心设计理念是：

- **框架与业务分离**：框架层（`src/tide`）提供通用基础设施能力，业务层（`pkg`）实现具体服务逻辑
- **领域驱动设计（DDD）**：业务模块采用 DDD 分层架构，职责清晰
- **插件机制**：通过 Plugin 机制灵活扩展框架能力（日志、监控、数据库、WebServer 等）
- **依赖注入**：通过 Provider 模式管理全局依赖，降低模块间耦合

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         cmd/                                     │
│              各业务服务的启动入口（main.py）                        │
│         组装插件、注册路由、启动服务                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
┌─────────────────────┐       ┌───────────────────────────────┐
│    src/tide          │       │          pkg/                  │
│   （框架核心层）      │       │      （业务逻辑层）             │
│                     │       │                               │
│  ┌───────────────┐  │       │  ┌─────────────────────────┐  │
│  │ TideApp       │  │       │  │ tide_date/              │  │
│  │ Command       │  │       │  │ tide_vllm/              │  │
│  │ Plugin        │  │       │  │ tide_vllm_wxvideo.../   │  │
│  │ Config        │  │       │  │ ...                     │  │
│  │ Provider      │  │       │  │                         │  │
│  │ Plugins/      │  │       │  │ 每个包遵循 DDD 分层：    │  │
│  │  ├─ log       │  │       │  │  application/           │  │
│  │  ├─ monitor   │  │       │  │  domain/                │  │
│  │  ├─ mysql     │  │       │  │  infrastructure/        │  │
│  │  ├─ redis     │  │       │  │  provider/              │  │
│  │  ├─ otel      │  │       │  └─────────────────────────┘  │
│  │  └─ web       │  │       │                               │
│  └───────────────┘  │       └───────────────────────────────┘
└─────────────────────┘
         ▲                               │
         │          业务层依赖框架层        │
         └─────────────────────────────────┘
```

**核心原则**：业务包（`pkg/*`）**依赖**框架（`src/tide`），框架**不依赖**业务包。业务包通过框架提供的 `Plugin`、`Provider`、`Config` 等机制接入框架。

## 3. 框架层：`src/tide`

框架层是 Tide 的通用底座，与具体业务逻辑无关，为所有业务服务提供共用的基础设施能力。

### 3.1 核心组件

| 组件 | 文件 | 职责 |
|---|---|---|
| **TideApp** | `app/application.py` | 应用程序主类，管理生命周期、插件加载和命令执行 |
| **Command** | `app/command.py` | 命令行支持，定义服务启动命令 |
| **Plugin** | `app/plugin.py` | 插件机制，定义插件接口和插件管理器 |
| **Config** | `config/config.py` | 配置管理（`TideConfig`、`WebConfig`、`LogConfig`、`DatabaseConfig`、`OpenTelemetryConfig`） |
| **Provider** | `provider/provider.py` | 全局依赖注入容器（单例模式） |

### 3.2 内置插件（`plugins/`）

框架内置了以下通用插件：

| 插件 | 职责 |
|---|---|
| `log` | 日志配置和管理 |
| `monitor` | 服务监控（健康检查、指标采集） |
| `mysql` | MySQL 数据库连接管理 |
| `redis` | Redis 连接管理 |
| `otel` | OpenTelemetry 链路追踪和指标上报 |
| `web` | Web Server 启动和路由管理 |

### 3.3 框架级 Provider

框架级 `Provider` 是一个**通用的全局依赖注入容器**，采用单例模式，提供 key-value 形式的依赖注册和获取：

```python
class Provider:
    """全局依赖注入容器（单例模式）"""

    def register(self, name: str, instance: Any) -> "Provider":
        """注册任意类型的依赖"""

    def get(self, name: str) -> Any:
        """按名称获取依赖"""

    def register_factory(self, name: str, factory: Callable) -> "Provider":
        """注册延迟创建的工厂函数"""

    # 常用快捷方法
    def set_mysql(self, client) -> None: ...
    def get_mysql(self) -> Optional[Any]: ...
    def set_redis(self, client) -> None: ...
    def get_redis(self) -> Optional[Any]: ...
    def set_tracer(self, tracer) -> None: ...
    def set_meter(self, meter) -> None: ...
```

> **特点**：与业务无关，只关心"存"和"取"，是一个万能的 key-value 容器。

## 4. 业务层：`pkg`

业务层包含具体服务的实现，每个子目录是一个独立的业务包，统一遵循 **DDD（领域驱动设计）** 分层架构。

### 4.1 现有业务包

| 业务包 | 用途 |
|---|---|
| `tide_date/` | 日期服务（框架示例模块） |
| `tide_vllm/` | vLLM 推理服务 |
| `tide_vllm_wxvideosceneaudit/` | 微信视频场景审核服务 |

### 4.2 DDD 四层架构

每个业务包内部统一遵循以下分层：

```
pkg/tide_xxx/
├── application/        # 应用层
│   ├── application.py  # 应用定义
│   └── xxx_handler.py  # Handler（用例编排）
├── domain/             # 领域层
│   └── xxx/
│       ├── entity.py       # 领域实体和值对象
│       ├── repository.py   # Repository 抽象接口
│       ├── factory.py      # 工厂方法
│       └── error.py        # 领域异常
├── infrastructure/     # 基础设施层
│   └── local/ (或 vllm/ 等)
│       └── xxx_repository.py  # Repository 具体实现
└── provider/           # 业务级依赖容器
    └── provider.py     # 业务模块的全局实例
```

各层职责：

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer（应用层）                │
│                      Handler / 用例编排                      │
│              接收请求 → 调用领域服务 → 返回响应                │
└─────────────────────────┬───────────────────────────────────┘
                          │ 调用
┌─────────────────────────▼───────────────────────────────────┐
│                      Domain Layer（领域层）                   │
│              Entity / Factory / Repository(ABC)              │
│          定义核心业务规则和抽象接口，不依赖任何技术实现          │
└─────────────────────────┬───────────────────────────────────┘
                          │ 实现接口
┌─────────────────────────▼───────────────────────────────────┐
│                  Infrastructure Layer（基础设施层）            │
│              Repository 实现 / 外部客户端 / 数据库访问          │
│           实现 Domain 层定义的接口，对接具体技术栈              │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 各层详解

#### 4.3.1 Domain 层 — 业务核心（"是什么"）

定义业务领域的核心模型和规则，**不依赖任何外部技术实现**。

以 `tide_date` 为例：

- **Entity（实体）**：`NowRequest`、`NowResponse`、`TideDate` — 定义业务数据结构和行为
- **Repository（接口）**：`DateRepository(ABC)` — 定义抽象接口，声明业务能做什么
- **Factory（工厂）**：创建领域实体的工厂方法
- **Error（异常）**：`ErrInternal` — 领域层专属异常

```python
# domain/date/repository.py — 只定义接口，不关心实现
class DateRepository(ABC):
    @abstractmethod
    async def now(self, req: NowRequest) -> NowResponse:
        pass
```

#### 4.3.2 Infrastructure 层 — 技术实现（"怎么做"）

实现 Domain 层定义的抽象接口，对接具体的技术栈（本地调用、数据库、远程 RPC 等）。

```python
# infrastructure/local/date_repository.py — 本地实现
class LocalDateRepository(Repository):
    async def now(self, req: NowRequest) -> NowResponse:
        return NowResponse(date=str(datetime.now()))
```

> **好处**：切换实现时（如从本地改为远程调用），只需替换 Infrastructure 层，Domain 层和 Application 层无需变动。

#### 4.3.3 Application 层 — 用例编排（"做什么"）

Handler 负责接收请求、调用领域服务、编排业务流程、返回响应。不包含核心业务规则。

#### 4.3.4 业务级 Provider — 模块内依赖容器

业务级 `Provider` 是**业务模块自己的全局实例容器**，存放该模块需要的特定依赖：

```python
# pkg/tide_date/provider/provider.py
@dataclass
class Provider:
    config: Dict[str, Any] = field(default_factory=dict)
    mysql: Optional[Any] = None
    redis: Optional[Any] = None
    resolver_service: Optional[Any] = None  # 业务特有的依赖
```

> **与框架级 Provider 的区别**：框架级 Provider 是通用的 key-value 容器，业务级 Provider 是强类型的、特定于某个业务模块的实例集合。

## 5. 框架级 vs 业务级组件对比

### 5.1 Provider 对比

| 维度 | `tide/provider` (框架级) | `pkg/*/provider` (业务级) |
|---|---|---|
| **通用性** | 通用，所有业务共享 | 特定于某个业务模块 |
| **实现方式** | 单例模式 + key-value 注册 | `@dataclass` + 强类型字段 |
| **存储内容** | MySQL、Redis、Tracer、Meter 等通用资源 | `config`、`resolver_service` 等业务特有实例 |
| **是否有业务逻辑** | ❌ 无 | ❌ 无（仅组装） |
| **Go 类比** | `provider/provider.go` | `pkg/*/provider.go` |

### 5.2 完整分层对比

| 维度 | `tide/provider` | `pkg/*/domain` | `pkg/*/infrastructure` | `pkg/*/provider` |
|---|---|---|---|---|
| **层级** | 框架层 | 业务领域层 | 业务基础设施层 | 业务组装层 |
| **职责** | 存取任意依赖 | 定义实体 + 抽象接口 | 实现抽象接口 | 存放业务全局实例 |
| **是否有业务逻辑** | ❌ | ✅ 核心业务规则 | ✅ 技术实现细节 | ❌ 仅组装 |

> **注意**：`src/tide` 框架层只有 `provider`，没有 `domain` 和 `infrastructure`，因为框架本身不包含任何业务逻辑。

## 6. 新增业务模块指南

创建一个新的业务模块，推荐遵循以下结构：

```
pkg/tide_xxx/
├── __init__.py
├── application/
│   ├── __init__.py
│   ├── application.py          # 应用定义
│   └── xxx_handler.py          # 业务 Handler
├── domain/
│   ├── __init__.py
│   └── xxx/
│       ├── __init__.py
│       ├── entity.py           # 领域实体
│       ├── repository.py       # Repository 接口（ABC）
│       ├── factory.py          # 工厂方法
│       └── error.py            # 领域异常
├── infrastructure/
│   ├── __init__.py
│   └── local/                  # 或 remote/、db/ 等
│       ├── __init__.py
│       └── xxx_repository.py   # Repository 实现
└── provider/
    ├── __init__.py
    └── provider.py             # 业务模块全局实例
```

同时在 `cmd/tide-xxx/` 下创建对应的服务入口和插件配置。

## 7. 设计参考

本框架的架构设计参考了以下项目：

- **Sea 框架（Go 版本）**：整体架构风格、Provider 模式、Plugin 机制
- **DDD（领域驱动设计）**：业务模块的分层架构
- **Clean Architecture**：依赖方向（外层依赖内层，Domain 层不依赖外部）
