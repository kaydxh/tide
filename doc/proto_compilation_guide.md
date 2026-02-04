# Proto 编译指南

本文档记录 Tide 项目中 Proto 文件编译相关的问题、原因及解决方案。

## 目录

- [编译命令](#编译命令)
- [常见问题](#常见问题)
  - [问题1: Import 路径找不到文件](#问题1-import-路径找不到文件)
  - [问题2: 类型未定义](#问题2-类型未定义)
- [Proto 文件规范](#proto-文件规范)

---

## 编译命令

```bash
# 检查编译工具是否安装
make proto-check

# 列出所有 proto 文件
make proto-list

# 编译所有 proto 文件
make proto

# 编译指定服务的 proto 文件
make proto-service SERVICE=tide_date/v1

# 清理生成的 proto 文件
make proto-clean
```

### 依赖工具

| 工具 | 安装方式 |
|------|---------|
| `protoc` | `brew install protobuf` (macOS) |
| `grpcio-tools` | `pip install grpcio-tools` |

---

## 常见问题

### 问题1: Import 路径找不到文件

#### 错误信息

```
api/protoapi-spec/types/error.proto: File not found.
api/protoapi_spec/tide_date/v1/api.proto:5:1: Import "api/protoapi-spec/types/error.proto" was not found or had errors.
```

#### 原因分析

Proto 文件中的 `import` 路径与实际目录结构不匹配：

| import 路径 | 实际路径 |
|------------|---------|
| `api/protoapi-spec/types/error.proto` | `api/protoapi_spec/types/error.proto` |

注意：路径中使用了 **短横线** (`protoapi-spec`)，但实际目录是 **下划线** (`protoapi_spec`)。

#### 解决方案

修改 proto 文件中的 import 语句，使用相对于 `PROTO_DIR` (`api/protoapi_spec`) 的路径：

```protobuf
// 错误写法
import "api/protoapi-spec/types/error.proto";

// 正确写法
import "types/error.proto";
```

> **说明**: Makefile 中配置了 `-I$(PROTO_DIR)`（即 `-Iapi/protoapi_spec`），因此 import 路径应该是相对于 `api/protoapi_spec` 目录的。

---

### 问题2: 类型未定义

#### 错误信息

```
api/protoapi_spec/tide_date/v1/api.proto:28:3: "types.Error" is not defined.
api/protoapi_spec/tide_date/v1/api.proto:38:3: "types.Error" is not defined.
```

#### 原因分析

引用的类型需要使用 **完整的 package 路径**。

`error.proto` 文件中定义的 package 是：

```protobuf
package tide.api.types;

message Error {
  int32 code = 1;
  string message = 2;
  string reason = 3;
}
```

因此引用时必须使用完整路径 `tide.api.types.Error`，而不是简写 `types.Error`。

#### 解决方案

使用完整的 package 路径引用类型：

```protobuf
// 错误写法
types.Error error = 1000;

// 正确写法
tide.api.types.Error error = 1000;
```

---

## Proto 文件规范

### 1. 目录结构

```
api/protoapi_spec/
├── types/                      # 公共类型定义
│   └── error.proto
├── tide_date/v1/               # tide_date 服务 v1 版本
│   └── api.proto
└── <service_name>/v1/          # 其他服务
    └── api.proto
```

### 2. Import 规范

- 使用相对于 `api/protoapi_spec` 的路径
- 公共类型放在 `types/` 目录下

```protobuf
// 导入公共类型
import "types/error.proto";

// 导入其他服务的 proto（如需要）
import "other_service/v1/api.proto";
```

### 3. Package 命名规范

```protobuf
// 公共类型
package tide.api.types;

// 服务 API
package tide.api.<service_name>;
```

### 4. 类型引用规范

引用其他 package 的类型时，使用完整路径：

```protobuf
// 引用公共 Error 类型
tide.api.types.Error error = 1000;
```

### 5. 完整示例

```protobuf
syntax = "proto3";

package tide.api.tidedate;

import "types/error.proto";

option java_package = "com.kaydxh.tide.api.tidedate.v1";
option java_multiple_files = true;

service TideDateService {
  rpc Now(NowRequest) returns (NowResponse) {};
}

message NowRequest {
  string request_id = 1 [json_name = "RequestId"];
}

message NowResponse {
  string request_id = 1 [json_name = "RequestId"];
  string date = 2 [json_name = "Date"];
  tide.api.types.Error error = 1000 [json_name = "Error"];
}
```

---

## 生成的文件

编译成功后，会在对应目录生成以下文件：

| 文件 | 说明 |
|------|------|
| `*_pb2.py` | Python message 类定义 |
| `*_pb2.pyi` | Python 类型提示文件 |
| `*_pb2_grpc.py` | gRPC service stub |

示例：

```
api/protoapi_spec/
├── types/
│   ├── error_pb2.py
│   ├── error_pb2.pyi
│   └── error_pb2_grpc.py
└── tide_date/v1/
    ├── api_pb2.py
    ├── api_pb2.pyi
    └── api_pb2_grpc.py
```

---

## 问题排查清单

遇到编译错误时，按以下顺序检查：

1. **检查工具安装**: `make proto-check`
2. **检查 import 路径**: 确保使用相对于 `api/protoapi_spec` 的路径
3. **检查目录名**: 确保路径中下划线/短横线一致
4. **检查类型引用**: 使用完整的 package 路径（如 `tide.api.types.Error`）
5. **检查 package 声明**: 确保被引用的 proto 文件 package 声明正确
