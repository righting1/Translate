# 异常处理改进文档

## 概述

本项目已实现全面的异常处理机制，使用自定义异常类型替代通用的 `Exception` 捕获，提供更精确的错误分类和用户友好的错误消息。

## 异常层次结构

### 基础异常类

```
TranslateAPIException (基类)
├── AIModelException (AI模型相关)
│   ├── ModelNotAvailableError (模型不可用)
│   ├── ModelAPIError (API调用错误)
│   ├── AuthenticationError (认证失败)
│   └── RateLimitError (速率限制)
├── InvalidRequestError (无效请求)
│   ├── TextTooLongError (文本过长)
│   └── EmptyTextError (空文本)
├── TaskNotFoundException (任务未找到)
├── TaskAlreadyCompletedError (任务已完成)
├── ConfigurationError (配置错误)
├── LangChainError (LangChain相关)
│   └── ChainNotFoundError (链未找到)
└── NetworkError (网络错误)
    └── TimeoutError (超时)
```

## 异常类详解

### 1. AIModelException 系列

#### ModelNotAvailableError
- **场景**：请求的AI模型未配置或不可用
- **状态码**：503
- **示例**：
```python
raise ModelNotAvailableError("gpt-4")
```

#### ModelAPIError
- **场景**：调用AI模型API时发生错误
- **状态码**：502
- **示例**：
```python
raise ModelAPIError("API调用失败", model_name="openai", original_error=e)
```

#### AuthenticationError
- **场景**：API密钥无效或认证失败
- **状态码**：401
- **示例**：
```python
raise AuthenticationError("Invalid API key", model_name="openai")
```

#### RateLimitError
- **场景**：超过API速率限制
- **状态码**：429
- **示例**：
```python
raise RateLimitError("Rate limit exceeded", model_name="openai")
```

### 2. InvalidRequestError 系列

#### EmptyTextError
- **场景**：提交的文本为空
- **状态码**：400
- **示例**：
```python
if not text or not text.strip():
    raise EmptyTextError()
```

#### TextTooLongError
- **场景**：文本超过最大长度限制
- **状态码**：400
- **示例**：
```python
if len(text) > 10000:
    raise TextTooLongError(len(text), 10000)
```

### 3. 任务管理异常

#### TaskNotFoundException
- **场景**：查询的任务ID不存在
- **状态码**：404
- **示例**：
```python
if not task:
    raise TaskNotFoundException(task_id)
```

#### TaskAlreadyCompletedError
- **场景**：尝试取消已完成的任务
- **状态码**：409
- **示例**：
```python
if task.status == TaskStatus.COMPLETED:
    raise TaskAlreadyCompletedError(task_id)
```

### 4. 网络异常

#### NetworkError
- **场景**：网络连接失败
- **状态码**：503
- **示例**：
```python
except httpx.NetworkError as e:
    raise NetworkError("连接失败", original_error=e)
```

#### TimeoutError
- **场景**：请求超时
- **状态码**：504
- **示例**：
```python
except httpx.TimeoutException:
    raise TimeoutError("请求超时", timeout_seconds=30)
```

## 使用指南

### 在路由处理器中使用

```python
from utils.exceptions import EmptyTextError, ModelAPIError

@router.post("/translate")
async def translate(req: TranslateRequest):
    # 输入验证
    if not req.text or not req.text.strip():
        raise EmptyTextError()
    
    # 业务逻辑...
    # 不需要try-except，让异常自然传播到全局处理器
```

### 在服务层使用

```python
from utils.exceptions import (
    ModelAPIError, 
    AuthenticationError,
    NetworkError,
    TimeoutError as CustomTimeoutError
)
import httpx
import logging

logger = logging.getLogger(__name__)

async def call_ai_model(self, prompt: str):
    if not self.api_key:
        raise AuthenticationError("API key not configured")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.api_url, json={"prompt": prompt})
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise CustomTimeoutError("API请求超时", timeout_seconds=30)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("API密钥无效")
        elif e.response.status_code == 429:
            raise RateLimitError("超过速率限制")
        else:
            raise ModelAPIError(f"API错误: {e.response.status_code}", original_error=e)
    except httpx.NetworkError as e:
        logger.error(f"网络错误: {e}")
        raise NetworkError("无法连接到AI服务", original_error=e)
    except Exception as e:
        # 只在最后捕获未知异常
        logger.exception("未预期的错误")
        raise ModelAPIError(f"未知错误: {str(e)}", original_error=e)
```

### 异常处理最佳实践

#### ✅ 推荐做法

1. **使用特定异常类型**
```python
# 好
if not api_key:
    raise AuthenticationError("API key missing")

# 避免
raise Exception("API key missing")
```

2. **让异常自然传播**
```python
# 好 - 让全局处理器统一处理
@router.post("/endpoint")
async def handler(req: Request):
    result = await service.process(req.text)
    return result

# 避免 - 过度捕获
@router.post("/endpoint")
async def handler(req: Request):
    try:
        result = await service.process(req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. **传递原始异常信息**
```python
# 好
except httpx.HTTPStatusError as e:
    raise ModelAPIError("API调用失败", original_error=e)

# 避免丢失上下文
except httpx.HTTPStatusError:
    raise ModelAPIError("API调用失败")
```

4. **添加有用的上下文**
```python
# 好
raise TaskNotFoundException(task_id)  # task_id会被添加到details

# 普通
raise HTTPException(404, "Not found")
```

#### ❌ 避免做法

1. **不要捕获所有异常然后静默**
```python
# 错误
try:
    result = await process()
except Exception:
    pass  # 问题被隐藏了
```

2. **不要暴露敏感信息**
```python
# 错误
except Exception as e:
    return {"error": f"Database error: {connection_string}"}
```

3. **不要在多处重复处理同一异常**
```python
# 避免
def service_method():
    try:
        ...
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/")
async def handler():
    try:
        service_method()
    except HTTPException as e:
        raise HTTPException(400, e.detail)  # 重复处理
```

## 错误响应格式

所有异常都会被转换为统一的JSON响应格式：

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

### 字段说明

- `error`: 用户友好的错误消息
- `status_code`: HTTP状态码
- `details`: 额外的错误详情（如字段名、原始错误类型等）
- `path`: 发生错误的API路径

## 测试

运行异常处理测试：

```bash
pytest tests/test_exception_handling.py -v
```

## 监控和日志

所有异常都会自动记录日志：

```python
# 自定义异常 - 记录为ERROR
logger.error(
    f"API Exception: {exc.message}",
    extra={
        "path": request.url.path,
        "status_code": exc.status_code,
        "details": exc.details
    }
)

# 未预期异常 - 记录完整堆栈
logger.exception("Unexpected error occurred", exc_info=exc)
```

## 迁移指南

### 从旧代码迁移

**Before:**
```python
@router.post("/translate")
async def translate(req: Request):
    try:
        result = await service.translate(req.text)
        return {"result": result}
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**After:**
```python
from utils.exceptions import EmptyTextError

@router.post("/translate")
async def translate(req: Request):
    if not req.text:
        raise EmptyTextError()
    
    # 让异常自然传播，全局处理器会处理
    result = await service.translate(req.text)
    return {"result": result}
```

## 扩展

添加新的异常类型：

```python
# utils/exceptions.py

class CustomBusinessError(TranslateAPIException):
    """自定义业务错误"""
    def __init__(self, message: str, business_code: str):
        super().__init__(message, status_code=400)
        self.details["business_code"] = business_code
```

使用：
```python
from utils.exceptions import CustomBusinessError

if invalid_business_logic:
    raise CustomBusinessError("业务规则违反", business_code="BIZ001")
```
