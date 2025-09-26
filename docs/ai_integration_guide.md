# AI大模型翻译服务使用指南

## 项目结构

该项目已经集成了AI大模型调用功能，主要包含以下组件：

```
project/
├── config.yaml              # 配置文件（包含AI模型配置）
├── .env.example             # 环境变量示例文件
├── prompt/                  # 提示词管理目录
│   ├── __init__.py
│   └── templates.py         # 统一的提示词模板
├── services/
│   ├── ai_model.py          # AI模型服务
│   └── translate.py         # 翻译服务（已更新）
└── api/translate/routes.py  # API路由（已更新）
```

## 配置说明

### 1. 环境变量设置

复制 `.env.example` 为 `.env` 并配置实际的API密钥：

```bash
# 阿里云DashScope API Key（通义千问）- 默认模型
DASHSCOPE_API_KEY=sk-your_dashscope_api_key_here

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# 智谱AI API Key
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
```

### 2. config.yaml 配置

已添加完整的AI模型配置：

```yaml
ai_model:
  default_model: "dashscope"  # 默认使用DashScope（通义千问）
  
  # 阿里云DashScope配置（通义千问）- 默认模型
  dashscope:
    api_key: "${DASHSCOPE_API_KEY}"
    base_url: "https://dashscope.aliyuncs.com/api/v1"
    model: "qwen-plus"
    temperature: 0.3
    max_tokens: 2000
    timeout: 30
  
  openai:
    api_key: "${OPENAI_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model: "gpt-3.5-turbo"
    temperature: 0.3
    max_tokens: 2000
    timeout: 30
  
  zhipuai:
    api_key: "${ZHIPUAI_API_KEY}"
    model: "glm-4"
    temperature: 0.3
    max_tokens: 2000
    timeout: 30
  
  # 支持更多模型...
```

## 支持的AI模型

- **阿里云DashScope (通义千问)**: 支持qwen系列模型，默认模型 ⭐
- **OpenAI GPT**: 支持官方API和兼容的第三方API
- **智谱AI**: 支持GLM系列模型
- **Ollama**: 支持本地部署模型
- **Azure OpenAI**: 支持Azure托管的OpenAI服务

## API接口

### 1. 获取可用模型
```http
GET /api/translate/models
```

### 2. 翻译接口

#### 中译英
```http
POST /api/translate/zh2en?model=openai
Content-Type: application/json

{
  "text": "你好，世界！"
}
```

#### 英译中
```http
POST /api/translate/en2zh?model=zhipuai
Content-Type: application/json

{
  "text": "Hello, world!"
}
```

#### 自动翻译（检测语言）
```http
POST /api/translate/auto?model=openai
Content-Type: application/json

{
  "text": "Hello, 世界！"
}
```

### 3. 总结接口

#### 基础总结
```http
POST /api/translate/summarize?model=openai&max_length=200
Content-Type: application/json

{
  "text": "很长的文本内容..."
}
```

#### 关键词总结
```http
POST /api/translate/keyword-summary?model=zhipuai&summary_length=100
Content-Type: application/json

{
  "text": "需要提取关键词的文本..."
}
```

#### 结构化总结
```http
POST /api/translate/structured-summary?model=openai&max_length=300
Content-Type: application/json

{
  "text": "需要结构化总结的文本..."
}
```

## 提示词管理

所有提示词都在 `prompt/templates.py` 中统一管理：

### 翻译提示词
- `ZH_TO_EN`: 中译英
- `EN_TO_ZH`: 英译中
- `AUTO_TRANSLATE`: 自动检测翻译

### 总结提示词
- `BASIC_SUMMARY`: 基础总结
- `KEYWORD_SUMMARY`: 关键词总结
- `STRUCTURED_SUMMARY`: 结构化总结

### 自定义提示词

可以轻松添加新的提示词模板：

```python
class CustomPrompts:
    CUSTOM_TASK = PromptTemplate(
        template="""你的自定义提示词模板
        
        用户输入：{text}
        
        请按要求处理。"""
    )
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python main.py
```

## 错误处理

服务包含完善的错误处理机制：
- API调用失败时返回错误信息
- 配置错误时使用默认配置
- 网络超时的处理
- 模型不可用时的降级处理

## 扩展指南

### 添加新的AI模型

1. 在 `services/ai_model.py` 中创建新的服务类
2. 继承 `AIModelBase` 基类
3. 实现 `chat_completion` 和 `text_completion` 方法
4. 在 `AIModelFactory` 中注册新服务
5. 在 `config.yaml` 中添加配置

### 添加新的功能

1. 在 `prompt/templates.py` 中添加提示词
2. 在 `services/translate.py` 中添加业务方法
3. 在 `api/translate/routes.py` 中添加API接口

这样的架构设计确保了：
- 配置的集中管理
- 提示词的统一维护
- 多种AI模型的支持
- 良好的扩展性和维护性