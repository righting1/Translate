from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class FeatureCode(str, Enum):
    zh2en = "zh2en"
    en2zh = "en2zh"
    summarize = "summarize"
    auto_translate = "auto_translate"
    keyword_summary = "keyword_summary"
    structured_summary = "structured_summary"


class Feature(BaseModel):
    code: FeatureCode
    name: str
    description: str


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


