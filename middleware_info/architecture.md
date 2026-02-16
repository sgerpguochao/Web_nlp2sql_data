# NL2SQL 数据生成系统 - 架构设计文档

## 一、系统整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户浏览器                                       │
│                          (访问 http://localhost:3000)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────────────────────┐
│                          前端 (React + Vite) :3000                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────────┐ │
│  │ ConfigurationPanel│  │  ProgressPanel  │  │         services/api.ts    │ │
│  │  (配置面板)       │  │  (进度展示)      │  │    (HTTP/WebSocket客户端)   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                              HTTP 8000 / WebSocket
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          后端 (FastAPI) :8000                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         app.py (主入口)                              │   │
│  │   • 路由注册 (api_router, ws_router, download_router)                │   │
│  │   • 生命周期管理 (启动/关闭清理 data 目录)                           │   │
│  │   • 静态文件服务 (frontend/dist)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                       │                                      │
│          ┌────────────────────────────┼────────────────────────────┐         │
│          ▼                            ▼                            ▼         │
│  ┌───────────────┐          ┌─────────────────┐          ┌───────────────┐  │
│  │ api/routes.py │          │ api/websocket.py│          │api/download.py│  │
│  │  (REST API)   │          │  (实时推送)     │          │  (文件下载)   │  │
│  └───────────────┘          └─────────────────┘          └───────────────┘  │
│          │                                                         │         │
│          ▼                                                         │         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     api/task_manager.py (任务管理器)                  │  │
│  │   • 单例模式管理任务状态                                              │  │
│  │   • 6步骤状态机: 连接DB→元数据→表卡片→规划→生成→验证→导出            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
┌───────────────────┐    ┌───────────────────────┐    ┌────────────────────────┐
│   MySQL 数据库     │    │   LLM 服务 (DeepSeek) │    │   文件系统 (data/)     │
│   (数据源)         │    │   (API调用)            │    │   (JSON/JSONL输出)    │
└───────────────────┘    └───────────────────────┘    └────────────────────────┘
```

---

## 二、模块划分与核心文件

### 2.1 前端 (`frontend/`)

| 模块/目录 | 核心文件 | 功能说明 |
|-----------|---------|---------|
| **入口** | `src/main.tsx` | React 应用入口，挂载 App 组件 |
| **主应用** | `src/App.tsx` | 主组件，协调配置面板、进度展示、WebSocket |
| **API 服务** | `src/services/api.ts` | HTTP 客户端 + WebSocket 客户端，连接后端 |
| **本地存储** | `src/services/storage.ts` | 保存/加载用户配置到 localStorage |
| **UI 组件** | `src/components/ui/*` | Radix UI 基础组件库 |
| **业务组件** | `src/components/ConfigurationPanel.tsx` | 数据库/LLM/生成配置表单 |
| | `src/components/ProgressPanel.tsx` | 进度条、日志展示面板 |
| **构建配置** | `vite.config.ts` | Vite 配置，端口 3000，host 0.0.0.0 |

### 2.2 后端 (`backend/`)

| 模块/目录 | 核心文件 | 功能说明 |
|-----------|---------|---------|
| **主入口** | `app.py` | FastAPI 应用，启动 uvicorn，路由注册 |
| **REST API** | `api/routes.py` | 核心业务 API：测试连接、启动任务、查询状态、获取日志 |
| **WebSocket** | `api/websocket.py` | 实时日志推送、状态同步 |
| **任务管理** | `api/task_manager.py` | 单例任务管理器，状态机控制 |
| **下载服务** | `api/download.py` | 生成数据文件下载接口 |
| **日志处理** | `api/log_handler.py` | WebSocket 日志处理器 |

### 2.3 核心处理模块 (`backend/modules/`)

| 模块 | 核心类/函数 | 功能说明 |
|------|------------|---------|
| **数据库连接** | `DatabaseConnector` 类 / `create_connector()` | 封装 MySQL/PostgreSQL 连接与查询 |
| **LLM 客户端** | `LLMClient` 类 / `create_llm_client()` | 封装 DeepSeek API 调用 |
| **元数据提取** | `metadata_extractor.py` | `MetadataExtractor` 类 / `extract_and_save_metadata()` | 从数据库提取表结构、字段、索引 |
| **表卡片生成** | `table_cards.py` | `TableCardsGenerator` 类 / `generate_and_save_table_cards()` | 调用 LLM 生成表的中文描述摘要 |
| **主题规划** | `planner.py` | `TopicPlanner` 类 / `generate_and_save_plan()` | **阶段 A**：调用 LLM 规划生成主题 |
| **样本生成** | `generator.py` | `SampleGenerator` 类 / `generate_and_save_samples()` | **阶段 B**：调用 LLM 生成 NL2SQL 样本 |
| **SQL 验证** | `validator.py` | `SQLValidator` 类 / `validate_and_save_samples()` | 执行 SQL 验证语法正确性 |
| **数据导出** | `exporter.py` | `DataExporter` 类 / `export_samples()` | 导出为 Alpaca/ShareGPT 等训练格式 |

---

## 三、数据流程与处理流水线

### 3.1 整体业务流程（6 步流水线）

```
用户点击"开始生成"
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: 连接数据库 (api/routes.py → modules/db_connector)                  │
│   • 建立 MySQL 连接                                                         │
│   • 获取表数量验证连接有效                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: 提取元数据 (modules/metadata_extractor)                             │
│   • 提取所有表的 DDL (CREATE TABLE 语句)                                    │
│   • 提取字段信息、索引、外键                                                 │
│   • 输出: ./data/metadata.json                                              │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: 生成表卡片 (modules/table_cards → LLM)                              │
│   • 对每个表调用 LLM 生成中文摘要/用途描述                                   │
│   • 输出: ./data/table_cards.json                                          │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: 规划主题 - LLM 阶段 A (modules/planner → LLM)                     │
│   • 将表卡片拼接为 prompt                                                   │
│   • 调用 LLM 规划生成主题（每个主题关联哪些表、生成多少样本）                │
│   • 输出: ./data/plan.json                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 5: 生成样本 - LLM 阶段 B (modules/generator → LLM)                    │
│   • 按主题逐个调用 LLM 生成 NL2SQL 对话                                     │
│   • prompt: 用户问题 + 数据库上下文                                         │
│   • output: SQL + 中文解释                                                  │
│   • 输出: ./data/samples_raw.jsonl                                         │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 6: SQL 验证 + 导出 (modules/validator + modules/exporter)            │
│   • 在数据库中执行生成的 SQL，验证语法/结果                                 │
│   • 导出为训练格式: Alpaca / ShareGPT / 自定义 JSONL                        │
│   • 输出: ./data/nl2sql.jsonl                                              │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
    生成完成，用户可下载训练数据
```

---

## 四、服务间依赖关系

### 4.1 前后端通信

| 方向 | 接口 | 说明 |
|------|------|------|
| 前端 → 后端 | `POST /api/test-db-connection` | 测试数据库连接 |
| 前端 → 后端 | `POST /api/test-llm-connection` | 测试 LLM 连接 |
| 前端 → 后端 | `POST /api/start-generation` | 启动生成任务 |
| 前端 → 后端 | `GET /api/status` | 查询任务状态 |
| 前端 → 后端 | `GET /api/logs` | 获取运行日志 |
| 前端 → 后端 | `GET /api/download/latest` | 下载生成的训练数据 |
| 前端 ↔ 后端 | `WebSocket /ws/logs` | 实时日志推送 |

### 4.2 后端内部模块调用链

```
api/routes.py (run_generation_task)
    │
    ├──▶ modules/db_connector.py (create_connector)
    │         │
    │         └── MySQL 数据库
    │
    ├──▶ modules/metadata_extractor.py
    │         └── LLM (可选，用于增强描述)
    │
    ├──▶ modules/table_cards.py ──▶ LLM (DeepSeek API)
    │
    ├──▶ modules/planner.py ──▶ LLM (阶段 A: 规划主题)
    │
    ├──▶ modules/generator.py ──▶ LLM (阶段 B: 生成样本)
    │
    ├──▶ modules/validator.py ──▶ DB (执行验证 SQL)
    │
    └──▶ modules/exporter.py ──▶ 文件系统 (JSONL)
```

---

## 五、外部服务集成

| 外部服务 | 集成方式 | 配置文件 |
|---------|---------|---------|
| **MySQL 数据库** | `modules/db_connector.py` (pymysql / pyodbc) | 用户通过前端表单输入 |
| **LLM (DeepSeek)** | `modules/llm_client.py` (requests 调用 REST API) | 用户通过前端表单输入 API Key |

---

## 六、关键设计模式

1. **任务管理器单例模式** (`task_manager.py`)：确保全局只有一个任务在运行
2. **工厂模式** (`create_connector`, `create_llm_client`)：根据配置动态创建数据库/LLM 客户端
3. **异步任务编排** (`asyncio.create_task`)：将耗时的生成任务放到后台执行，避免阻塞 API
4. **WebSocket 实时推送**：通过 `log_handler.py` 将日志实时推送到前端

---

## 七、目录结构汇总

```
Web_nlp2sql_data/
├── backend/                    # 后端服务
│   ├── app.py                  # FastAPI 主入口
│   ├── auto_nl2sql.py          # CLI 主程序（非 Web 模式）
│   ├── api/
│   │   ├── routes.py           # REST API 路由
│   │   ├── websocket.py        # WebSocket 处理
│   │   ├── task_manager.py     # 任务状态管理
│   │   ├── download.py        # 文件下载
│   │   └── log_handler.py     # 日志推送
│   └── modules/                # 核心处理模块
│       ├── db_connector.py     # 数据库连接
│       ├── llm_client.py       # LLM 调用
│       ├── metadata_extractor.py
│       ├── table_cards.py
│       ├── planner.py          # 阶段 A
│       ├── generator.py        # 阶段 B
│       ├── validator.py
│       └── exporter.py
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── main.tsx           # React 入口
│   │   ├── App.tsx            # 主组件
│   │   ├── services/api.ts    # API 客户端
│   │   ├── components/
│   │   │   ├── ConfigurationPanel.tsx
│   │   │   └── ProgressPanel.tsx
│   │   └── components/ui/     # Radix UI 组件
│   ├── vite.config.ts         # Vite 配置
│   └── package.json
│
└── data/                      # 生成数据目录（运行时创建）
    ├── metadata.json
    ├── table_cards.json
    ├── plan.json
    ├── samples_raw.jsonl
    ├── samples_valid.jsonl
    └── nl2sql.jsonl           # 最终训练数据
```

---

## 八、系统流程图

### 8.1 用户交互流程

```
┌──────────┐    1.填写配置     ┌──────────────────┐    2.点击开始    ┌─────────┐
│  用户浏览器 │ ──────────────▶ │  Configuration   │ ──────────────▶ │  App   │
└──────────┘                   │    Panel         │                  │Component│
                                └──────────────────┘                  └────┬────┘
                                                                         │
                                      3.POST /api/start-generation        │
                                      ┌──────────────────────────────────┘
                                      ▼
                               ┌─────────────┐
                               │  后端 API   │
                               │ (FastAPI)   │
                               └──────┬──────┘
                                      │
                                      ▼ 异步执行
                               ┌─────────────┐
                               │ TaskManager │ ◀──── 6步流水线
                               │  (状态机)   │
                               └──────┬──────┘
                                      │
                   ┌─────────────────┼─────────────────┐
                   │                 │                 │
                   ▼                 ▼                 ▼
            ┌───────────┐    ┌───────────┐    ┌───────────┐
            │ WebSocket │    │   文件    │    │   状态    │
            │  实时日志  │    │  下载API  │    │  查询API  │
            └─────┬─────┘    └───────────┘    └───────────┘
                  │
                  ▼
            ┌──────────┐
            │ 前端进度  │
            │  面板更新 │
            └──────────┘
```

### 8.2 LLM 两阶段生成流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LLM 两阶段生成                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  阶段 A: 主题规划 (planner.py)                                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ 输入: 表卡片 (table_cards.json)                                     │   │
│  │      + 生成数量配置 (total_samples)                                  │   │
│  │      + 每主题表数量范围 (min/max_tables_per_topic)                   │   │
│  │                                                                       │   │
│  │ Prompt 示例:                                                         │   │
│  │ "你是一个数据库专家。根据以下表结构，             │   │
│  │  规划 {total_samples} 个主题用于生成 NL2SQL 训练数据。             │   │
│  │  每个主题需要 {min}-{max} 个表..."                                  │   │
│  │                                                                       │   │
│  │ 输出: 主题列表 (plan.json)                                           │   │
│  │   [                                                                    │   │
│  │     {"topic": "销售数据分析", "tables": ["orders", "products"],     │   │
│  │      "sample_count": 30},                                            │   │
│  │     {"topic": "用户行为分析", "tables": ["users", "events"], ...}   │   │
│  │   ]                                                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  阶段 B: 样本生成 (generator.py)                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ 输入: 主题 + 对应表 + 表结构 (metadata.json)                         │   │
│  │                                                                       │   │
│  │ 对每个主题，调用 LLM 生成多个 NL2SQL 对话                            │   │
│  │                                                                       │   │
│  │ Prompt 示例:                                                         │   │
│  │ "根据数据库表结构:                                                    │   │
│  │   orders(order_id, customer_id, amount, create_time...)            │   │
│  │   products(product_id, name, price...)                             │   │
│  │                                                                       │   │
│  │ 用户问题: 统计每个客户的订单总额                                       │   │
│  │                                                                       │   │
│  │ 生成: SQL + 中文问题 + 解释"                                        │   │
│  │                                                                       │   │
│  │ 输出: samples_raw.jsonl                                             │   │
│  │   {"instruction": "统计每个客户的订单总额",                           │   │
│  │    "input": "...",                                                  │   │
│  │    "output": "SELECT customer_id, SUM(amount) FROM orders..."}      │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*文档生成时间: 2026-02-16*
