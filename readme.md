# Translate API

一个基于 FastAPI 的翻译与总结服务，内置同步接口、LangChain 能力、异步任务队列与 SSE 流式输出，并提供统一的功能发现与提示词校验接口，便于前后端联调与扩展。

## 功能一览（Endpoints）

- 基础
  - 健康检查：GET `/api/v1/health`
  - 问候：GET `/api/v1/greet/{name}`

- 功能发现与工具
  - 特性列表（枚举化）：GET `/api/translate/features`
  - 可用模型：GET `/api/translate/models`
  - 提示词类型：GET `/api/translate/prompt-types`
  - 校验提示词：POST `/api/translate/validate-prompt`（JSON：`{ "category": "translation|summarization", "prompt_type": "..." }`）

- 同步接口（推荐简单入手）
  - 中译英：POST `/api/translate/zh2en`
  - 英译中：POST `/api/translate/en2zh`
  - 自动翻译：POST `/api/translate/auto`
  - 总结：POST `/api/translate/summarize?max_length=200`
  - 关键词总结：POST `/api/translate/keyword-summary?summary_length=80`
  - 结构化总结：POST `/api/translate/structured-summary?max_length=200`
  - 说明：body 支持可选 `model` 字段；为空或不传时，会使用配置中的默认模型

- LangChain 能力
  - 通用翻译：POST `/api/translate/langchain/translate`
  - 中译英：POST `/api/translate/langchain/zh2en`
  - 英译中：POST `/api/translate/langchain/en2zh`
  - 总结：POST `/api/translate/langchain/summarize`
  - 链管理：
    - 列表：GET `/api/translate/langchain/chains/list`
    - 查看：POST `/api/translate/langchain/chains/inspect/{chain_name}`（例如：`basic_summary_chain`）
    - 清空记忆：DELETE `/api/translate/langchain/chains/clear`

- 异步任务（提交 -> 轮询 -> 结果）
  - 提交：
    - 中译英：POST `/api/translate/async/zh2en`
    - 英译中：POST `/api/translate/async/en2zh`
    - 总结：POST `/api/translate/async/summarize?max_length=200`
    - 关键词总结：POST `/api/translate/async/keyword-summary?summary_length=80`
    - 结构化总结：POST `/api/translate/async/structured-summary?max_length=200`
  - 查询：
    - 状态：GET `/api/translate/async/status/{task_id}`
    - 结果：GET `/api/translate/async/result/{task_id}`
    - 便捷别名（已新增）：GET `/api/translate/async/{task_id}`（已完成则直接返回结果，未完成返回状态与指引）
  - 列表与统计：
    - 任务列表：GET `/api/translate/async/tasks?status=&limit=20`
    - 统计：GET `/api/translate/async/stats`
  - 取消任务：DELETE `/api/translate/async/cancel/{task_id}`
  - 说明：提交返回体包含 `poll_url` 与 `result_url`，可直接点击使用

- 流式（SSE）
  - 中译英：POST `/api/translate/stream/zh2en`
  - 英译中：POST `/api/translate/stream/en2zh`
  - 总结：POST `/api/translate/stream/summarize`
  - 说明：请设置 `Accept: text/event-stream`

## 快速开始

1) 安装依赖（建议 Python 3.11+）

```bash
pip install -r requirements.txt
```

2) 配置 `config.yaml`（关键：AI 模型）

项目已内置 DashScope（通义千问）示例，支持“OpenAI 兼容模式”与“原生模式”自动识别。请优先使用环境变量注入密钥：

```yaml
app:
  app_name: "Translate API"
  debug: true
  host: "127.0.0.1"
  port: 8000
  reload: true
  log_level: "info"
  version: "0.1.0"

ai_model:
  default_model: "dashscope"
  dashscope:
    service_type: "dashscope"
    api_key: "${DASHSCOPE_API_KEY}"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 兼容模式（自动适配）
    model: "qwen-plus"
    temperature: 0.3
    max_tokens: 2000
    timeout: 60
```

3) 启动服务

```bash
uvicorn main:app --reload
# 或
python main.py
```

打开浏览器：
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

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

## 项目结构（简要）

```
.
├── api/
│   ├── translate/
│   │   └── routes.py                  # 同步接口 + LangChain + 工具接口
│   ├── async_tasks/
│   │   └── routes.py                  # 异步任务提交/状态/结果/统计/便捷别名
│   ├── stream/
│   │   └── routes.py                  # SSE 流式接口
│   └── v1/
│       └── routes.py                  # 健康检查与问候
├── core/
│   └── config/__init__.py             # 配置加载（YAML + 环境变量替换）
├── schemas/
│   └── translate.py                   # 枚举/请求/响应模型（Feature/Endpoint/HttpMethod 等）
├── services/
│   ├── ai_model.py                    # OpenAI/DashScope/Ollama/AzureOpenAI 抽象与实现
│   ├── langchain_service.py           # LangChain 基础设施（服务注册/链执行/流式等）
│   ├── langchain_translate.py         # 基于 LangChain 的翻译/总结服务（预置链）
│   └── async_task_manager.py          # 任务管理（队列/并发/清理/TTL）
├── utils/
│   ├── exceptions.py                  # 自定义异常类型定义
│   └── error_handlers.py              # 全局异常处理器
├── tests/
│   ├── test_api.py
│   └── test_exception_handling.py     # 异常处理测试
├── docs/
│   └── exception_handling.md          # 异常处理使用指南
├── api_all.http                       # 全量 HTTP 请求集合
├── api_test.http                      # 精简 HTTP 请求集合
├── demo_exception_handling.py         # 异常处理演示脚本
├── main.py                            # 应用入口
├── config.yaml                        # 配置文件
├── requirements.txt
└── mkdocs.yml
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




