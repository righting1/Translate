from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class FeatureCode(str, Enum):
    zh2en = "zh2en"
    en2zh = "en2zh"
    summarize = "summarize"
    auto_translate = "auto_translate"
    keyword_summary = "keyword_summary"
    structured_summary = "structured_summary"
    # LangChain 专用功能
    langchain_translate = "langchain_translate"
    langchain_zh2en = "langchain_zh2en"
    langchain_en2zh = "langchain_en2zh"
    langchain_summarize = "langchain_summarize"
    # 异步任务功能
    async_zh2en = "async_zh2en"
    async_en2zh = "async_en2zh"
    async_summarize = "async_summarize"
    async_keyword_summary = "async_keyword_summary"
    async_structured_summary = "async_structured_summary"
    # 流式返回功能（SSE）
    stream_zh2en = "stream_zh2en"
    stream_en2zh = "stream_en2zh"
    stream_summarize = "stream_summarize"


class FeatureName(str, Enum):
    # 基础同步
    EN2ZH = "英译中"
    SUMMARIZE = "总结摘要"
    AUTO_TRANSLATE = "自动翻译"
    KEYWORD_SUMMARY = "关键词总结"
    STRUCTURED_SUMMARY = "结构化总结"

    # LangChain
    LC_TRANSLATE = "LangChain 通用翻译"
    LC_ZH2EN = "LangChain 中译英"
    LC_EN2ZH = "LangChain 英译中"
    LC_SUMMARIZE = "LangChain 总结"

    # 异步任务
    ASYNC_ZH2EN = "异步 中译英"
    ASYNC_EN2ZH = "异步 英译中"
    ASYNC_SUMMARIZE = "异步 总结"
    ASYNC_KEYWORD_SUMMARY = "异步 关键词总结"
    ASYNC_STRUCTURED_SUMMARY = "异步 结构化总结"
    ASYNC_STATUS = "异步 任务状态查询"
    ASYNC_RESULT = "异步 任务结果获取"
    ASYNC_CANCEL = "异步 取消任务"
    ASYNC_TASKS = "异步 任务列表"
    ASYNC_STATS = "异步 任务统计"

    # 流式（SSE）
    STREAM_ZH2EN = "流式 中译英"
    STREAM_EN2ZH = "流式 英译中"
    STREAM_SUMMARIZE = "流式 总结"


class FeatureDescription(str, Enum):
    # 基础同步
    EN2ZH = "将英文翻译为中文"
    SUMMARIZE = "对输入文本进行简要总结"
    AUTO_TRANSLATE = "自动检测语言并翻译"
    KEYWORD_SUMMARY = "提取关键词并总结"
    STRUCTURED_SUMMARY = "按结构化格式总结"

    # LangChain
    LC_TRANSLATE = "LangChain 框架下的通用翻译"
    LC_ZH2EN = "LangChain 中译英专用接口"
    LC_EN2ZH = "LangChain 英译中专用接口"
    LC_SUMMARIZE = "LangChain 文本总结"

    # 异步任务
    ASYNC_ZH2EN = "提交任务后轮询获取结果"
    ASYNC_EN2ZH = "提交任务后轮询获取结果"
    ASYNC_SUMMARIZE = "提交任务后轮询获取结果"
    ASYNC_KEYWORD_SUMMARY = "提交任务后轮询获取结果"
    ASYNC_STRUCTURED_SUMMARY = "提交任务后轮询获取结果"
    ASYNC_STATUS = "根据 task_id 查询任务状态"
    ASYNC_RESULT = "根据 task_id 获取任务结果"
    ASYNC_CANCEL = "取消进行中的任务"
    ASYNC_TASKS = "列出任务（可按状态过滤）"
    ASYNC_STATS = "统计任务数量与状态"

    # 流式（SSE）
    STREAM_ZH2EN = "SSE 实时返回翻译结果"
    STREAM_EN2ZH = "SSE 实时返回翻译结果"
    STREAM_SUMMARIZE = "SSE 实时返回总结结果"


class Feature(BaseModel):
    code: FeatureCode
    name: "FeatureName"
    description: "FeatureDescription"
    url: "Endpoint"
    method: "HttpMethod" = None  # default set below


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class Endpoint(str, Enum):
    # 基础同步
    TRANSLATE_ZH2EN = "/api/translate/zh2en"
    TRANSLATE_EN2ZH = "/api/translate/en2zh"
    TRANSLATE_SUMMARIZE = "/api/translate/summarize"
    TRANSLATE_AUTO = "/api/translate/auto"
    TRANSLATE_KEYWORD_SUMMARY = "/api/translate/keyword-summary"
    TRANSLATE_STRUCTURED_SUMMARY = "/api/translate/structured-summary"

    # LangChain
    LC_TRANSLATE = "/api/translate/langchain/translate"
    LC_ZH2EN = "/api/translate/langchain/zh2en"
    LC_EN2ZH = "/api/translate/langchain/en2zh"
    LC_SUMMARIZE = "/api/translate/langchain/summarize"

    # 异步任务 - 提交
    ASYNC_ZH2EN = "/api/translate/async/zh2en"
    ASYNC_EN2ZH = "/api/translate/async/en2zh"
    ASYNC_SUMMARIZE = "/api/translate/async/summarize"
    ASYNC_KEYWORD_SUMMARY = "/api/translate/async/keyword-summary"
    ASYNC_STRUCTURED_SUMMARY = "/api/translate/async/structured-summary"
    # 异步任务 - 管理
    ASYNC_STATUS = "/api/translate/async/status/{task_id}"
    ASYNC_RESULT = "/api/translate/async/result/{task_id}"
    ASYNC_CANCEL = "/api/translate/async/cancel/{task_id}"
    ASYNC_TASKS = "/api/translate/async/tasks"
    ASYNC_STATS = "/api/translate/async/stats"

    # 流式（SSE）
    STREAM_ZH2EN = "/api/translate/stream/zh2en"
    STREAM_EN2ZH = "/api/translate/stream/en2zh"
    STREAM_SUMMARIZE = "/api/translate/stream/summarize"


# set default for method now that HttpMethod exists
Feature.model_fields["method"].default = HttpMethod.POST


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    target_language: str = Field(default="英文", description="目标语言")
    source_language: Optional[str] = Field(default=None, description="源语言，None表示自动检测")
    context: Optional[str] = Field(default=None, description="翻译上下文")
    task: FeatureCode = FeatureCode.zh2en
    model: Optional[str] = None


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: Optional[str] = None
    target_language: str
    result: str  # 保持向后兼容性
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    
    def __init__(self, **data):
        if 'translated_text' in data and 'result' not in data:
            data['result'] = data['translated_text']
        elif 'result' in data and 'translated_text' not in data:
            data['translated_text'] = data['result']
        super().__init__(**data)


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_length: Optional[int] = Field(default=100, description="总结最大长度")
    context: Optional[str] = Field(default=None, description="总结上下文")
    model: Optional[str] = None


class SummarizeResponse(BaseModel):
    summary: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None




class FeatureListResponse(BaseModel):
    features: List[Feature]


class SimpleTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    model: Optional[str] = None


class ValidatePromptRequest(BaseModel):
    category: str
    prompt_type: str


class AsyncTaskConfig(BaseModel):
    """异步任务配置"""
    max_retries: Optional[int] = Field(default=3, ge=0, le=10, description="最大重试次数")
    enable_notifications: Optional[bool] = Field(default=False, description="是否启用失败通知")
    save_failure_details: Optional[bool] = Field(default=True, description="是否保存失败详情到文件")
    notification_email: Optional[str] = Field(default=None, description="失败通知邮箱")
    custom_callback_name: Optional[str] = Field(default=None, description="自定义回调函数名称")


class AsyncTaskRequest(BaseModel):
    """增强的异步任务请求"""
    text: str = Field(..., min_length=1)
    model: Optional[str] = None
    config: Optional[AsyncTaskConfig] = Field(default_factory=AsyncTaskConfig)


