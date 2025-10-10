# Translate API

一个基于 FastAPI 的翻译与总结服务，内置同步接口、LangChain 能力、异步任务队列与 SSE 流式输出，并提供统一的功能发现与提示词校验接口，便于前后端联调与扩展。

## 功能特性

### 🚀 核心功能

- **多模型AI支持**: 支持OpenAI、智谱AI、阿里云DashScope等多种AI模型（配置各大厂商的url,apikey等参数即可使用）
- **同步翻译**: 实时翻译接口，支持中英文互译
- **异步任务**: 后台任务处理，支持大文本翻译和复杂总结
- **失败回调**: 异步任务失败时自动执行回调函数，支持重试、通知、日志记录等
- **流式输出**: SSE流式响应，实时获取翻译结果
- **LangChain集成**: 内置多种预置链，支持复杂文本处理
- **智能摘要**: 支持关键词摘要、结构化摘要等多种总结方式

### 📋 主要接口

#### 基础接口

- 健康检查：`GET /api/v1/health`
- 问候接口：`GET /api/v1/greet/{name}`

#### 功能发现

- 特性列表：`GET /api/translate/features`
- 可用模型：`GET /api/translate/models`
- 提示词类型：`GET /api/translate/prompt-types`
- 提示词校验：`POST /api/translate/validate-prompt`

#### 同步翻译接口

- 中译英：`POST /api/translate/zh2en`
- 英译中：`POST /api/translate/en2zh`
- 自动翻译：`POST /api/translate/auto`
- 文本摘要：`POST /api/translate/summarize`
- 关键词摘要：`POST /api/translate/keyword-summary`
- 结构化摘要：`POST /api/translate/structured-summary`

#### LangChain能力

- 通用翻译：`POST /api/translate/langchain/translate`
- 链管理：`GET /api/translate/langchain/chains/list`
- 链检查：`POST /api/translate/langchain/chains/inspect/{chain_name}`
- 清除记忆：`DELETE /api/translate/langchain/chains/clear`

#### 异步任务接口

- 任务提交：`POST /api/translate/async/{type}`
- 任务状态：`GET /api/translate/async/status/{task_id}`
- 任务结果：`GET /api/translate/async/result/{task_id}`
- 任务列表：`GET /api/translate/async/tasks`
- 任务统计：`GET /api/translate/async/stats`
- 取消任务：`DELETE /api/translate/async/cancel/{task_id}`

#### 失败回调管理

- 可用回调：`GET /api/translate/async/callbacks/available`
- 测试回调：`POST /api/translate/async/callbacks/test?callback_name={name}`

#### 流式接口

- 流式翻译：`POST /api/translate/stream/{type}`
- 支持SSE (Server-Sent Events) 实时输出

## 环境配置

项目使用 `.env` 文件管理敏感配置和环境变量。环境变量通过 `{}` 占位符在 `config.yaml` 中自动插值。

### 1. 环境变量配置

编辑 `.env` 文件，配置AI模型相关参数：

```bash
# AI模型配置
# OpenAI配置 - 请替换为您的真实API密钥
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# 阿里云DashScope配置 - 请替换为您的真实API密钥
DASHSCOPE_API_KEY=sk-7a3acac23fd24d7eb382f7196096eeae
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 2. 配置文件自动插值

项目支持在 `config.yaml` 中使用 `{VARIABLE_NAME}` 格式从环境变量获取配置：
我主要是把密钥等信息放在.env文件里面了

```yaml
# config.yaml 示例
ai_services:
  openai:
    api_key: "{OPENAI_API_KEY}"
    base_url: "{OPENAI_BASE_URL}"
  
  dashscope:
    api_key: "{DASHSCOPE_API_KEY}"
    base_url: "{DASHSCOPE_BASE_URL}"
```

### 3. 核心环境变量

| 变量名 | 描述 | 示例值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-xxx...` | 可选 |
| `OPENAI_BASE_URL` | OpenAI API基础URL | `https://api.openai.com/v1` | 可选 |
| `DASHSCOPE_API_KEY` | 阿里云DashScope API密钥 | `sk-xxx...` | 推荐 |
| `DASHSCOPE_BASE_URL` | DashScope API基础URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 推荐 |

### 4. 配置说明

- **必填项**: 至少配置一个AI服务的API密钥才能正常使用翻译功能
- **推荐配置**: DashScope（通义千问）作为主要AI服务，稳定性和中文支持较好
- **多服务支持**: 可同时配置多个AI服务，系统会根据配置自动选择可用服务
- **环境变量优先级**: 环境变量配置优先级高于硬编码配置

## 快速开始

### Docker 一键部署

项目已内置 Dockerfile 和 docker-compose.yml，支持一键容器化部署。

#### 1. 构建镜像（如仅需单容器）

```bash
docker build -t translate-api .
```

#### 2. 启动容器（单容器方式）

```bash
docker run --env-file .env -p 8000:8000 --name translate-api translate-api
```

#### 3. 推荐：使用 docker-compose 管理

```bash
docker-compose up -d
```

#### 4. 停止与重启

```bash
docker-compose stop
docker-compose start
docker-compose down   # 停止并移除容器
```

#### 5. 日志查看

```bash
docker-compose logs -f
```

#### 6. 环境变量与持久化

- 请编辑 `.env` 文件，配置 API 密钥等参数
- 日志文件默认挂载到主机目录（app.log, app.err.log）

#### 7. 端口与 API 访问

- 容器默认监听 8000 端口，主机访问 http://localhost:8000/docs


#### 8. Docker API 测试

部署完成后，使用内置的 API 测试脚本验证服务是否正常运行：

##### 基础测试命令

```bash
# 基础测试（测试所有API端点）
python tests/docker_api_test.py

# 指定 API 基础URL
python tests/docker_api_test.py --base http://localhost:8000

# 设置超时时间（秒）
python tests/docker_api_test.py --timeout 30

# 显示详细输出
python tests/docker_api_test.py --verbose
```

##### 跳过特定测试类型

```bash
# 跳过流式测试（如果网络较慢）
python tests/docker_api_test.py --skip-stream

# 跳过 LangChain 测试
python tests/docker_api_test.py --skip-langchain

# 跳过异步任务测试
python tests/docker_api_test.py --skip-async

# 组合跳过多种测试
python tests/docker_api_test.py --skip-stream --skip-async
```

##### 使用环境变量配置测试

```bash
# Windows PowerShell
$env:DOCKER_API_BASE="http://localhost:8000"
$env:DOCKER_API_TIMEOUT="20"
$env:DOCKER_SKIP_STREAM="true"
python tests/docker_api_test.py

# Linux/macOS
export DOCKER_API_BASE=http://localhost:8000
export DOCKER_API_TIMEOUT=20
export DOCKER_SKIP_STREAM=true
python tests/docker_api_test.py
```

##### 测试结果示例

```bash
$ python tests/docker_api_test.py
== Translate API 端到端测试 ==
Base URL: http://localhost:8000
[PASS] GET /api/v1/health
[PASS] GET /api/v1/greet/{name} - Hello Tester
[PASS] GET /api/translate/models - models=['dashscope']
Using model: dashscope
[PASS] GET /api/translate/features - features=22
...
[PASS] POST /api/translate/stream/summarize - chunks=5
== 测试结果 ==
Passed: 39
Failed: 0
Skipped: 0
```

---

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**

   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置AI模型API密钥
   ```

3. **启动应用**

   选择以下任一种方式启动：

   #### 方式1：后台运行（推荐）

   - Windows PowerShell:

     ```powershell
     .\start_background.ps1 start
     ```

   - Windows CMD:

     ```bat
     start_background.bat start
     ```

   - Linux/macOS:

     ```bash
     chmod +x ./start_background.sh
     ./start_background.sh start
     ```

   停止/状态/重启：

   - PowerShell

     ```powershell
     .\start_background.ps1 stop
     .\start_background.ps1 status
     .\start_background.ps1 restart
     ```

   - CMD

     ```bat
     start_background.bat stop
     start_background.bat status
     start_background.bat restart
     ```

   - Linux/macOS

     ```bash
     ./start_background.sh stop
     ./start_background.sh status
     ./start_background.sh restart
     ```



   #### 方式2：前台运行（开发调试）

  ```bash
   # 直接使用uvicorn
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

   # 或使用Python脚本
   python run.py start
   ```

#### 方式3：Python管理脚本

```bash
   # 查看所有功能
   python run.py --help

   # 完整流程 (检查→安装→启动)
   python run.py all

  # 仅运行测试
  python run.py test
```

### 访问应用

启动成功后，打开浏览器访问：

- **API文档**: `http://127.0.0.1:8000/docs`
- **交互式API**: `http://127.0.0.1:8000/redoc`
- **健康检查**: `http://127.0.0.1:8000/api/v1/health`

## 异步任务失败回调

项目内置了完善的异步任务失败处理机制，支持自动重试、失败通知、日志记录等功能。

### 🔧 核心特性

- **自动重试**: 支持指数退避重试策略，可配置最大重试次数
- **智能重试判断**: 根据错误类型自动判断是否适合重试（网络错误可重试，参数错误不重试）
- **失败回调**: 支持任务级和全局失败回调函数
- **通知机制**: 支持邮件、Webhook、Slack等多种通知方式
- **详细日志**: 自动记录失败详情、错误堆栈、重试历史等

### 📝 使用方式

#### 1. 基础配置

创建异步任务时可以配置失败处理参数：

```json
{
  "text": "要翻译的文本",
  "model": "openai",
  "config": {
    "max_retries": 3,
    "enable_notifications": true,
    "save_failure_details": true,
    "notification_email": "admin@example.com",
    "custom_callback_name": "slack_notification"
  }
}
```

#### 2. 可用回调函数

| 回调函数名 | 功能描述 |
|-----------|----------|
| `log_failure` | 记录失败信息到应用日志 |
| `save_failure_details` | 保存详细失败信息到JSON文件 |
| `send_notification` | 发送失败通知（支持多种渠道） |
| `cleanup_task_data` | 清理失败任务的临时数据 |
| `slack_notification` | 发送Slack通知（需配置） |
| `database_log` | 记录失败信息到数据库（需配置） |

#### 3. API接口

```bash
# 获取可用回调函数列表
GET /api/translate/async/callbacks/available

# 测试回调函数
POST /api/translate/async/callbacks/test?callback_name=log_failure
```

#### 4. 测试失败回调

使用内置测试脚本验证失败回调功能：

```bash
# 运行失败回调测试
python tests/test_failure_callbacks.py

# 检查生成的日志文件
ls logs/failures/
ls logs/email_notifications/
```

### 🛠️ 自定义回调

可以通过代码注册自定义失败回调函数：

```python
from app.services.async_task_manager import task_manager

async def custom_failure_callback(failure_data):
    # 自定义失败处理逻辑
    print(f"任务 {failure_data['task_id']} 失败: {failure_data['error_message']}")

# 注册全局回调
task_manager.add_global_failure_callback(custom_failure_callback)

# 创建带特定回调的任务
task_id = task_manager.create_task(
    task_type=TaskType.ZH2EN,
    input_data={"text": "Hello"},
    failure_callback=custom_failure_callback
)
```

### 📊 失败统计

系统自动收集失败统计信息：

- 失败日志文件：`logs/failures/`
- 统计数据：`logs/failure_stats.json`
- 通知记录：`logs/notifications.txt`

## 测试

项目包含完整的测试套件，覆盖API接口、异步任务、异常处理等功能，支持单元测试和集成测试。

### 运行测试

#### 1. pytest 单元测试

```bash
# 运行所有单元测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_api.py
python -m pytest tests/test_async_tasks.py
python -m pytest tests/test_exception_handling.py
python -m pytest tests/test_langchain_integration.py
python -m pytest tests/test_streaming.py
python -m pytest tests/test_async_cancel.py

# 运行带详细输出的测试
python -m pytest tests/ -v --tb=short

# 运行覆盖率测试
python -m pytest tests/ --cov=app --cov-report=html
```

#### 2. Docker API 集成测试

```bash
# 运行完整的Docker API测试（推荐）
python tests/docker_api_test.py --base http://localhost:8000

# 跳过某些测试类型
python tests/docker_api_test.py --skip-stream --skip-langchain --skip-async

# 指定超时时间
python tests/docker_api_test.py --timeout 30

# 使用环境变量配置
export DOCKER_API_BASE=http://localhost:8000
export DOCKER_SKIP_STREAM=true
python tests/docker_api_test.py
```

### 测试覆盖范围

#### ✅ **单元测试覆盖**
- **基础API测试** (`test_api.py`): 健康检查、问候接口、基本翻译功能
- **异步任务测试** (`test_async_tasks.py`): 任务提交、状态轮询、结果获取的端到端测试
- **任务取消测试** (`test_async_cancel.py`): 异步任务取消机制和状态管理
- **异常处理测试** (`test_exception_handling.py`): 各种错误情况的处理和响应格式验证
- **LangChain集成测试** (`test_langchain_integration.py`): LangChain API端点和链管理功能
- **流式接口测试** (`test_streaming.py`): SSE流式输出的数据接收和格式验证

#### ✅ **集成测试覆盖**
- **完整API测试** (`docker_api_test.py`): 38个测试用例覆盖所有API端点
  - V1 API: 健康检查、问候接口
  - 翻译功能: 中英互译、自动翻译、各种摘要功能
  - LangChain: 翻译、链管理、记忆清除
  - 异步任务: 提交、查询、取消、统计
  - 流式接口: 实时翻译和摘要输出
  - 功能发现: 特性列表、模型信息、提示词验证

#### ✅ **Mock和隔离**
- **AI服务Mock** (`conftest.py`): 自动Mock所有AI服务调用，避免依赖外部API
- **服务隔离**: 测试不需要真实的API密钥即可运行
- **环境独立**: 每个测试使用独立的测试客户端

### 测试文件结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest配置和全局fixtures
├── docker_api_test.py             # Docker API完整集成测试
├── test_api.py                    # 基础API接口单元测试
├── test_async_tasks.py            # 异步任务功能测试
├── test_async_cancel.py           # 任务取消机制测试
├── test_exception_handling.py     # 异常处理和错误响应测试
├── test_langchain_integration.py  # LangChain功能集成测试
└── test_streaming.py              # SSE流式接口测试
```

### 测试环境配置

#### 环境变量支持

```bash
# Docker API测试配置
DOCKER_API_BASE=http://localhost:8000    # API基础URL
DOCKER_API_TIMEOUT=20                    # 请求超时时间
DOCKER_TEST_MODEL=                       # 指定测试模型
DOCKER_SKIP_STREAM=false                 # 跳过流式测试
DOCKER_SKIP_LANGCHAIN=false              # 跳过LangChain测试
DOCKER_SKIP_ASYNC=false                  # 跳过异步测试
```

#### Mock服务特性

- **自动AI服务Mock**: 所有测试自动使用模拟的AI服务响应
- **一致性保证**: Mock响应格式与真实API保持一致
- **无外部依赖**: 测试可在没有网络连接的环境中运行

## HTTP 测试（VS Code REST Client）

项目内置了请求集合：

- `api_test.http`：精简版

使用提示：

- 顶部变量 `@baseUrl` 例如 `http://localhost:8000`
- JSON 请求必须携带 `Content-Type: application/json`
- SSE 需设置 `Accept: text/event-stream`
- 提交异步任务后，请优先使用响应中的 `result_url`/`poll_url`

## 常见问题（Troubleshooting）

- 422 Unprocessable Entity / JSON decode error：
  - 大多因为缺少或错误的 JSON 体、或未设置 `Content-Type: application/json`

- 404 Not Found：
  - 路径写错（例如把 `/result/{task_id}` 写成 `/ {task_id}`）
  - 已提供便捷别名：GET `/api/translate/async/{task_id}`

- "No service available for text generation"：
  - 过去由空字符串模型名导致（`"model": ""`），现已在路由与服务层统一回退到默认模型

- DashScope 相关：
  - 已支持兼容模式与原生模式自动选择接口路径；如遇 401/404，请检查 `DASHSCOPE_API_KEY` 与 `base_url`

## 项目结构

```text
.
├── app/                           # 应用主目录
│   ├── main.py                   # FastAPI应用入口
│   ├── api/                      # API路由模块
│   │   ├── v1/
│   │   │   └── routes.py         # 基础接口（健康检查、问候）
│   │   ├── translate/
│   │   │   └── routes.py         # 翻译相关接口（同步、LangChain、工具）
│   │   ├── async_tasks/
│   │   │   └── routes.py         # 异步任务接口
│   │   └── stream/
│   │       └── routes.py         # 流式接口（SSE）
│   ├── core/
│   │   └── config/
│   │       └── __init__.py       # 配置管理（YAML + 环境变量）
│   ├── models/                   # 数据模型
│   ├── schemas/                  # Pydantic数据模型
│   │   └── translate.py          # 翻译相关的数据模型
│   ├── services/                 # 业务逻辑服务
│   │   ├── ai_model.py           # AI模型抽象层
│   │   ├── langchain_service.py  # LangChain服务
│   │   ├── langchain_translate.py # LangChain翻译服务
│   │   ├── async_task_manager.py # 异步任务管理器
│   │   └── translate.py          # 翻译服务
│   ├── utils/                    # 工具函数
│   │   ├── error_handlers.py     # 全局异常处理器
│   │   ├── exceptions.py         # 自定义异常类
│   │   └── logging_config.py     # 日志配置
│   └── __init__.py
├── tests/                        # 测试文件
│   ├── __init__.py
│   ├── conftest.py               # 测试配置
│   ├── test_api.py               # API接口测试
│   ├── test_async_tasks.py       # 异步任务测试
│   ├── test_async_cancel.py      # 任务取消测试
│   ├── test_exception_handling.py # 异常处理测试
│   ├── test_langchain_integration.py # LangChain集成测试
│   ├── test_streaming.py         # 流式接口测试
│   └── test_translate.py         # 翻译功能测试
├── docs/                         # 文档
│   ├── async_task_testing_guide.md # 异步任务测试指南
│   ├── exception_handling.md     # 异常处理指南
│   └── index.md                  # MkDocs首页
├── scripts/                      # 脚本目录（可选）
├── .env.example                  # 环境变量模板
├── .env                          # 环境变量配置（需手动创建）
├── config.yaml                   # 应用配置
├── requirements.txt              # Python依赖
├── pyrightconfig.json            # Pyright配置
├── pytest.ini                    # Pytest配置
├── mkdocs.yml                    # MkDocs配置
├── README.md                     # 项目说明
├── RUNNING_GUIDE.md              # 运行指南
├── run.py                        # Python管理脚本
├── start.bat                     # Windows前台启动脚本
├── start.sh                      # Linux/macOS启动脚本
├── start_background.bat          # Windows后台启动脚本
├── start_background.ps1          # PowerShell后台启动脚本
├── api_test.http                 # HTTP测试文件（简版）
├── api_all.http                  # HTTP测试文件（全量）
├── demo_exception_handling.py    # 异常处理演示
└── main.py                       # 开发环境入口（可选）
```

## 异常处理

项目实现了完善的异常处理机制，使用特定的异常类型替代通用的 `Exception` 捕获。

### 主要异常类型

- **请求验证类** (400)
  - `EmptyTextError` - 文本为空
  - `TextTooLongError` - 文本超过长度限制
  
- **认证授权类** (401, 429)
  - `AuthenticationError` - API密钥无效
  - `RateLimitError` - 超过速率限制
  
- **资源未找到类** (404)
  - `TaskNotFoundException` - 任务不存在
  - `ChainNotFoundError` - LangChain链不存在
  
- **服务错误类** (502, 503, 504)
  - `ModelAPIError` - AI模型API调用失败
  - `ModelNotAvailableError` - 模型不可用
  - `NetworkError` - 网络连接错误
  - `TimeoutError` - 请求超时

### 错误响应格式

所有API错误都返回统一的JSON格式：

```json
{
  "error": "Task 'abc123' not found",
  "status_code": 404,
  "details": {
    "task_id": "abc123"
  },
  "path": "/api/translate/async/status/abc123"
}
```

### 使用示例

```python
from utils.exceptions import EmptyTextError, TaskNotFoundException

# 路由层
@router.post("/translate")
async def translate(req: Request):
    if not req.text or not req.text.strip():
        raise EmptyTextError()
    
    result = await service.translate(req.text)
    return {"result": result}

# 服务层
async def get_task(self, task_id: str):
    task = self._tasks.get(task_id)
    if not task:
        raise TaskNotFoundException(task_id)
    return task
```

### 相关文档

- 📖 详细使用指南（异常相关）: [docs/exception_handling.md](docs/exception_handling.md)
- 📖 异步任务测试指南: [docs/async_task_testing_guide.md](docs/async_task_testing_guide.md)
- 📖 运行指南: [RUNNING_GUIDE.md](RUNNING_GUIDE.md)

## 开发与部署

### 本地开发

1. 克隆项目
2. 配置环境变量
3. 安装依赖
4. 运行测试
5. 启动开发服务器

### 生产部署

#### 使用Docker

```bash
docker-compose up -d
```


### 监控和日志

- 应用日志保存在 `app.log`
