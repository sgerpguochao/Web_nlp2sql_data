# NL2SQL 后端服务接口文档

## 一、接口概览

| 基础URL | 说明 |
|---------|------|
| `http://localhost:8000` | 后端服务地址 |

---

## 二、通用说明

### 请求头
```http
Content-Type: application/json
```

### 响应格式
所有接口返回 JSON 格式数据。

---

## 三、接口清单

### 3.1 健康检查

#### GET /health

检查后端服务是否正常运行。

**响应示例：**
```json
{
  "status": "ok",
  "service": "nl2sql-api",
  "version": "1.0.0"
}
```

---

### 3.2 获取任务状态

#### GET /api/status

获取当前生成任务的状态。

**响应示例：**
```json
{
  "task_id": null,
  "status": "idle",
  "current_step": 0,
  "total_steps": 6,
  "step_name": "",
  "progress": 0,
  "error_message": "",
  "start_time": null,
  "end_time": null,
  "details": {}
}
```

**状态说明：**
| status | 说明 |
|--------|------|
| `idle` | 空闲，无任务运行 |
| `running` | 任务运行中 |
| `completed` | 任务已完成 |
| `failed` | 任务失败 |
| `cancelled` | 任务已取消 |

**步骤说明：**
| step | 说明 |
|------|------|
| 1 | 连接数据库 |
| 2 | 提取元数据 |
| 3 | 生成表卡片 |
| 4 | 规划主题 |
| 5 | 生成SQL样本 |
| 6 | 验证SQL / 导出数据 |

---

### 3.3 获取日志

#### GET /api/logs

获取任务运行日志。

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `limit` | int | 100 | 返回的日志数量 |

**响应示例：**
```json
{
  "logs": [
    {
      "level": "info",
      "message": "正在连接数据库...",
      "timestamp": "2026-02-18T01:00:00"
    }
  ]
}
```

---

### 3.4 测试数据库连接

#### POST /api/test-db-connection

测试数据库连接是否成功。

**请求体：**
```json
{
  "type": "mysql",
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "password": "csd123456",
  "database": "ai_sales_data"
}
```

**字段说明：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 数据库类型：`mysql`、`postgresql` |
| `host` | string | 是 | 数据库主机地址 |
| `port` | int | 是 | 数据库端口 |
| `user` | string | 是 | 数据库用户名 |
| `password` | string | 是 | 数据库密码 |
| `database` | string | 是 | 数据库名称 |

**响应示例：**
```json
{
  "success": true,
  "message": "数据库连接成功",
  "tables_count": 6
}
```

---

### 3.5 测试 LLM 连接

#### POST /api/test-llm-connection

测试 LLM API 连接是否成功。

**请求体：**
```json
{
  "api_base": "https://api.deepseek.com",
  "api_key": "sk-xxx",
  "model_name": "deepseek-chat",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 4096,
  "timeout": 60,
  "max_retries": 3
}
```

**字段说明：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `api_base` | string | 是 | LLM API 基础地址 |
| `api_key` | string | 是 | LLM API Key |
| `model_name` | string | 是 | 模型名称 |
| `temperature` | float | 否 | 采样温度，默认 0.7 |
| `top_p` | float | 否 | Top P 采样，默认 0.9 |
| `max_tokens` | int | 否 | 最大 token 数，默认 4096 |
| `timeout` | int | 否 | 请求超时秒数，默认 60 |
| `max_retries` | int | 否 | 最大重试次数，默认 3 |

**响应示例：**
```json
{
  "success": true,
  "message": "LLM连接成功",
  "response": "连接成功"
}
```

---

### 3.6 启动生成任务

#### POST /api/start-generation

启动 NL2SQL 数据生成任务。

**请求体：**
```json
{
  "db": {
    "type": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "csd123456",
    "database": "ai_sales_data"
  },
  "llm": {
    "api_base": "https://api.deepseek.com",
    "api_key": "sk-xxx",
    "model_name": "deepseek-chat",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 4096,
    "timeout": 60,
    "max_retries": 3
  },
  "generate": {
    "total_samples": 100,
    "dialect": "mysql",
    "output_path": "./data/nl2sql.jsonl",
    "output_format": "alpaca",
    "enable_validation": true,
    "min_tables_per_topic": 3,
    "max_tables_per_topic": 8
  }
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `db` | object | 是 | 数据库配置（同 3.4） |
| `llm` | object | 是 | LLM 配置（同 3.5） |
| `generate` | object | 是 | 生成配置 |

**generate 子字段：**
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `total_samples` | int | 100 | 生成样本总数 |
| `dialect` | string | "mysql" | SQL 方言：`mysql`、`postgresql` |
| `output_path` | string | "./data/nl2sql.jsonl" | 输出文件路径 |
| `output_format` | string | "alpaca" | 输出格式：`alpaca`、`sharegpt` |
| `enable_validation` | bool | true | 是否启用 SQL 验证 |
| `min_tables_per_topic` | int | 3 | 每个主题最少使用表数 |
| `max_tables_per_topic` | int | 8 | 每个主题最多使用表数 |

**响应示例：**
```json
{
  "success": true,
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "任务已启动"
}
```

---

### 3.7 取消任务

#### POST /api/cancel

取消当前正在运行的生成任务。

**响应示例：**
```json
{
  "success": true,
  "message": "任务已取消"
}
```

---

### 3.8 下载生成的数据

#### GET /api/download/latest

下载最新生成的训练数据文件。

**响应：**
- Content-Type: `application/jsonl`
- Content-Disposition: `attachment; filename=nl2sql.jsonl`

---

### 3.9 下载 RAG 训练数据包

#### GET /api/download/rag

下载 RAG 训练数据包（包含 ddl.jsonl、doc.jsonl、plan.jsonl、sql_parse.jsonl）。

**响应：**
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename=ddl_mysql.zip`

---

### 3.10 下载指定文件

#### GET /api/download/{filename}

下载指定的中间文件。

**路径参数：**
| filename | 说明 |
|----------|------|
| `metadata.json` | 数据库表结构元数据 |
| `table_cards.json` | 表卡片摘要 |
| `plan.json` | 主题规划 |
| `samples_raw.jsonl` | 原始生成的样本 |
| `samples_valid.jsonl` | 验证后的样本 |
| `nl2sql.jsonl` | 最终训练数据 |
| `nl2sql_alpaca.jsonl` | Alpaca 格式 |
| `nl2sql_sharegpt.jsonl` | ShareGPT 格式 |

---

### 3.11 WebSocket 实时日志

#### WebSocket /ws/logs

建立 WebSocket 连接，实时接收任务日志和进度更新。

**连接地址：**
```
ws://localhost:8000/ws/logs
```

**接收消息格式：**
```json
{
  "type": "log",
  "level": "info",
  "message": "正在连接数据库...",
  "timestamp": "2026-02-18T01:00:00"
}
```

```json
{
  "type": "progress",
  "step": 1,
  "total_steps": 6,
  "step_name": "连接数据库",
  "progress": 16
}
```

---

## 四、错误响应

所有接口错误时返回标准 HTTP 状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式：**
```json
{
  "detail": "错误描述信息"
}
```

---

## 五、使用示例

### Python requests 示例

```python
import requests

API_BASE = "http://localhost:8000"

# 测试数据库连接
db_config = {
    "type": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "csd123456",
    "database": "ai_sales_data",
}
r = requests.post(f"{API_BASE}/api/test-db-connection", json=db_config)
print(r.json())

# 启动生成任务
task_config = {
    "db": db_config,
    "llm": {
        "api_base": "https://api.deepseek.com",
        "api_key": "sk-xxx",
        "model_name": "deepseek-chat",
    },
    "generate": {
        "total_samples": 100,
    }
}
r = requests.post(f"{API_BASE}/api/start-generation", json=task_config)
print(r.json())
```

---

*文档生成时间: 2026-02-18*
