# LangChain 中英文翻译接口更新说明

## 概述
本次更新为翻译服务添加了专门的 LangChain 中英文翻译接口，参考 Dedicated 版本的设计，使用两个独立的请求处理中英文互相翻译。

## 新增接口

### 1. LangChain 中文翻译成英文
- **URL**: `POST /api/translate/langchain/zh2en`
- **功能**: 使用 LangChain 框架将中文翻译成英文
- **请求体**: `SimpleTextRequest`
- **查询参数**:
  - `model` (可选): AI模型名称
  - `use_chains` (可选): 是否使用预构建的链，默认为 `true`

#### 示例请求：
```http
POST http://127.0.0.1:8000/api/translate/langchain/zh2en?model=dashscope
Content-Type: application/json

{
  "text": "你好，世界！这是一个使用LangChain框架的翻译测试。"
}
```

### 2. LangChain 英文翻译成中文
- **URL**: `POST /api/translate/langchain/en2zh`
- **功能**: 使用 LangChain 框架将英文翻译成中文
- **请求体**: `SimpleTextRequest`
- **查询参数**:
  - `model` (可选): AI模型名称
  - `use_chains` (可选): 是否使用预构建的链，默认为 `true`

#### 示例请求：
```http
POST http://127.0.0.1:8000/api/translate/langchain/en2zh?model=dashscope
Content-Type: application/json

{
  "text": "Hello, world! This is a translation test using LangChain framework."
}
```

## 响应格式
两个接口都返回 `TranslateResponse` 格式：

```json
{
  "translated_text": "翻译结果",
  "source_language": "中文",
  "target_language": "英文",
  "result": "翻译结果",
  "model": "使用的模型名称"
}
```

## 功能特性

### 1. 链式调用支持
- 默认使用预构建的 LangChain 链 (`use_chains=true`)
- 可以禁用链式调用使用直接模式 (`use_chains=false`)

### 2. 模型选择
- 支持通过 `model` 查询参数指定 AI 模型
- 支持的模型: `dashscope`, `openai`, `zhipuai`, `ollama`, `azure`
- 如果不指定模型，使用默认的 `langchain_default`

### 3. 错误处理
- 完整的异常捕获和错误返回
- 详细的错误日志记录
- HTTP 500 状态码表示服务器错误

## 与现有接口的区别

### 与 Dedicated 接口的比较
- **相似点**: 
  - 使用相同的请求/响应格式 (`SimpleTextRequest`/`TranslateResponse`)
  - 提供专门的中英文翻译接口
  - 支持模型选择
  
- **不同点**:
  - LangChain 版本支持链式调用 (`use_chains` 参数)
  - LangChain 版本使用 LangChain 框架的高级功能
  - 路径前缀为 `/langchain/` 以区分版本

### 与通用 LangChain 接口的比较
- **通用接口**: `/api/translate/langchain/translate` - 需要指定目标语言
- **专门接口**: `/api/translate/langchain/zh2en`, `/api/translate/langchain/en2zh` - 固定翻译方向

## 测试用例
在 `test_main.http` 文件中已添加完整的测试用例：

1. **基础翻译测试**
2. **带模型参数的翻译测试**  
3. **禁用链式调用的翻译测试**

## 使用建议

### 1. 性能优化
- 对于频繁的中英文翻译，建议使用链式调用 (`use_chains=true`)
- 对于实验性翻译，可以禁用链式调用测试不同配置

### 2. 模型选择
- `dashscope`: 推荐用于中文翻译，效果较好
- `openai`: 适合高质量翻译，但需要 API 密钥
- `zhipuai`: 国内模型，适合中文处理

### 3. 错误处理
- 始终检查响应状态码
- 处理可能的网络超时和模型服务不可用情况

## 配置要求

确保 `config.yaml` 中配置了相应的 AI 模型服务：

```yaml
ai_models:
  dashscope:
    api_key: "your_dashscope_api_key"
    base_url: "https://dashscope.aliyuncs.com/api/v1"
    model: "qwen-turbo"
  # ... 其他模型配置
```

## 下一步计划

1. **性能监控**: 添加翻译质量和速度监控
2. **缓存机制**: 实现翻译结果缓存
3. **批量翻译**: 支持批量文本翻译
4. **自定义提示**: 支持用户自定义翻译提示模板