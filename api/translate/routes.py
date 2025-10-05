from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from schemas.translate import (
    TranslateRequest,
    TranslateResponse,
    SummarizeRequest,
    SummarizeResponse,
    Feature,
    FeatureListResponse,
    SimpleTextRequest,
)
from services.translate import TranslationService
from services.langchain_translate import LangChainTranslationService
from services.async_task_manager import task_manager, TaskType, TaskStatus
from schemas.translate import FeatureCode, Endpoint, HttpMethod, FeatureName, FeatureDescription, ValidatePromptRequest

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/translate", tags=["translate"])


def get_translation_service(req: TranslateRequest) -> TranslationService:
    return TranslationService(model_name=req.model)


def get_simple_translation_service() -> TranslationService:
    return TranslationService()


def get_langchain_service() -> LangChainTranslationService:
    return LangChainTranslationService()


#根据参数选择要执行的任务
@router.post("/run", response_model=TranslateResponse)
async def run_translate(
    req: TranslateRequest,
    service: TranslationService = Depends(get_translation_service),
) -> TranslateResponse:
    if req.task == FeatureCode.zh2en:
        result = await service.zh2en(req.text)
        target_lang = "英文"
        source_lang = "中文"
    elif req.task == FeatureCode.en2zh:
        result = await service.en2zh(req.text)
        target_lang = "中文"
        source_lang = "英文"
    elif req.task == FeatureCode.auto_translate:
        result = await service.auto_translate(req.text)
        target_lang = "自动检测"
        source_lang = "自动检测"
    elif req.task == FeatureCode.keyword_summary:
        result = await service.keyword_summary(req.text)
        target_lang = "关键词总结"
        source_lang = "原文"
    elif req.task == FeatureCode.structured_summary:
        result = await service.structured_summary(req.text)
        target_lang = "结构化总结"
        source_lang = "原文"
    else:  # FeatureCode.summarize
        result = await service.summarize(req.text)
        target_lang = "总结"
        source_lang = "原文"

    return TranslateResponse(
        result=result,
        translated_text=result,
        target_language=target_lang,
        source_language=source_lang,
        model=service.model_name
    )


@router.get("/features", response_model=FeatureListResponse)
async def list_features() -> FeatureListResponse:
    features = [
        # 基础同步功能
    Feature(code=FeatureCode.en2zh, name=FeatureName.EN2ZH, description=FeatureDescription.EN2ZH, url=Endpoint.TRANSLATE_EN2ZH, method=HttpMethod.POST),
    Feature(code=FeatureCode.summarize, name=FeatureName.SUMMARIZE, description=FeatureDescription.SUMMARIZE, url=Endpoint.TRANSLATE_SUMMARIZE, method=HttpMethod.POST),
    Feature(code=FeatureCode.auto_translate, name=FeatureName.AUTO_TRANSLATE, description=FeatureDescription.AUTO_TRANSLATE, url=Endpoint.TRANSLATE_AUTO, method=HttpMethod.POST),
    Feature(code=FeatureCode.keyword_summary, name=FeatureName.KEYWORD_SUMMARY, description=FeatureDescription.KEYWORD_SUMMARY, url=Endpoint.TRANSLATE_KEYWORD_SUMMARY, method=HttpMethod.POST),
    Feature(code=FeatureCode.structured_summary, name=FeatureName.STRUCTURED_SUMMARY, description=FeatureDescription.STRUCTURED_SUMMARY, url=Endpoint.TRANSLATE_STRUCTURED_SUMMARY, method=HttpMethod.POST),

        # LangChain 功能
    Feature(code=FeatureCode.langchain_translate, name=FeatureName.LC_TRANSLATE, description=FeatureDescription.LC_TRANSLATE, url=Endpoint.LC_TRANSLATE, method=HttpMethod.POST),
    Feature(code=FeatureCode.langchain_zh2en, name=FeatureName.LC_ZH2EN, description=FeatureDescription.LC_ZH2EN, url=Endpoint.LC_ZH2EN, method=HttpMethod.POST),
    Feature(code=FeatureCode.langchain_en2zh, name=FeatureName.LC_EN2ZH, description=FeatureDescription.LC_EN2ZH, url=Endpoint.LC_EN2ZH, method=HttpMethod.POST),
    Feature(code=FeatureCode.langchain_summarize, name=FeatureName.LC_SUMMARIZE, description=FeatureDescription.LC_SUMMARIZE, url=Endpoint.LC_SUMMARIZE, method=HttpMethod.POST),

        # 异步任务功能
    Feature(code=FeatureCode.async_zh2en, name=FeatureName.ASYNC_ZH2EN, description=FeatureDescription.ASYNC_ZH2EN, url=Endpoint.ASYNC_ZH2EN, method=HttpMethod.POST),
    Feature(code=FeatureCode.async_en2zh, name=FeatureName.ASYNC_EN2ZH, description=FeatureDescription.ASYNC_EN2ZH, url=Endpoint.ASYNC_EN2ZH, method=HttpMethod.POST),
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_SUMMARIZE, description=FeatureDescription.ASYNC_SUMMARIZE, url=Endpoint.ASYNC_SUMMARIZE, method=HttpMethod.POST),
    Feature(code=FeatureCode.async_keyword_summary, name=FeatureName.ASYNC_KEYWORD_SUMMARY, description=FeatureDescription.ASYNC_KEYWORD_SUMMARY, url=Endpoint.ASYNC_KEYWORD_SUMMARY, method=HttpMethod.POST),
    Feature(code=FeatureCode.async_structured_summary, name=FeatureName.ASYNC_STRUCTURED_SUMMARY, description=FeatureDescription.ASYNC_STRUCTURED_SUMMARY, url=Endpoint.ASYNC_STRUCTURED_SUMMARY, method=HttpMethod.POST),

        # 异步任务管理附属接口（非功能任务本身，可用于前端集成展示）
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_STATUS, description=FeatureDescription.ASYNC_STATUS, url=Endpoint.ASYNC_STATUS, method=HttpMethod.GET),
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_RESULT, description=FeatureDescription.ASYNC_RESULT, url=Endpoint.ASYNC_RESULT, method=HttpMethod.GET),
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_CANCEL, description=FeatureDescription.ASYNC_CANCEL, url=Endpoint.ASYNC_CANCEL, method=HttpMethod.DELETE),
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_TASKS, description=FeatureDescription.ASYNC_TASKS, url=Endpoint.ASYNC_TASKS, method=HttpMethod.GET),
    Feature(code=FeatureCode.async_summarize, name=FeatureName.ASYNC_STATS, description=FeatureDescription.ASYNC_STATS, url=Endpoint.ASYNC_STATS, method=HttpMethod.GET),

        # 流式返回（SSE）功能
    Feature(code=FeatureCode.stream_zh2en, name=FeatureName.STREAM_ZH2EN, description=FeatureDescription.STREAM_ZH2EN, url=Endpoint.STREAM_ZH2EN, method=HttpMethod.POST),
    Feature(code=FeatureCode.stream_en2zh, name=FeatureName.STREAM_EN2ZH, description=FeatureDescription.STREAM_EN2ZH, url=Endpoint.STREAM_EN2ZH, method=HttpMethod.POST),
    Feature(code=FeatureCode.stream_summarize, name=FeatureName.STREAM_SUMMARIZE, description=FeatureDescription.STREAM_SUMMARIZE, url=Endpoint.STREAM_SUMMARIZE, method=HttpMethod.POST),
    ]
    return FeatureListResponse(features=features)



#可以使用的模型
@router.get("/models")
async def list_available_models():
    """获取可用的AI模型列表"""
    try:
        service = TranslationService()
        models = service.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


#获得提示词（翻译，总结，系统提示词）
@router.get("/prompt-types")
async def list_prompt_types():
    """获取所有可用的提示词类型"""
    try:
        from prompt.utils import prompt_helper
        prompt_info = prompt_helper.get_prompt_type_info()
        return {
            "prompt_types": prompt_info,
            "categories": list(prompt_info.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prompt types: {str(e)}")


# LangChain版本的API端点
@router.post("/langchain/translate", response_model=TranslateResponse)
async def langchain_translate(
    request: TranslateRequest,
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    使用LangChain框架进行翻译
    支持链式调用和对话上下文管理
    """
    try:
        if hasattr(service, 'model_name') and request.model:
            service.model_name = request.model
        if hasattr(service, 'use_chains'):
            service.use_chains = True
            
        result = await service.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
            context=request.context
        )
        return TranslateResponse(
            translated_text=result,
            source_language=request.source_language or "auto",
            target_language=request.target_language
        )
    except Exception as e:
        logger.error(f"LangChain translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# LangChain版本的中英文翻译接口
@router.post("/langchain/zh2en", response_model=TranslateResponse)
async def langchain_translate_zh2en(
    req: SimpleTextRequest,
    service: LangChainTranslationService = Depends(get_langchain_service)
) -> TranslateResponse:
    """
    使用LangChain框架将中文翻译成英文
    """
    try:
        if hasattr(service, 'model_name') and getattr(req, 'model', None):
            service.model_name = req.model
        if hasattr(service, 'use_chains'):
            service.use_chains = True
            
        result = await service.zh2en(req.text)
        return TranslateResponse(
            result=result, 
            translated_text=result,
            target_language="英文",
            source_language="中文",
            model=req.model or "langchain_default"
        )
    except Exception as e:
        logger.error(f"LangChain zh2en translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain/en2zh", response_model=TranslateResponse)
async def langchain_translate_en2zh(
    req: SimpleTextRequest,
    service: LangChainTranslationService = Depends(get_langchain_service)
) -> TranslateResponse:
    """
    使用LangChain框架将英文翻译成中文
    """
    try:
        if hasattr(service, 'model_name') and getattr(req, 'model', None):
            service.model_name = req.model
        if hasattr(service, 'use_chains'):
            service.use_chains = True
            
        result = await service.en2zh(req.text)
        return TranslateResponse(
            result=result, 
            translated_text=result,
            target_language="中文",
            source_language="英文",
            model=req.model or "langchain_default"
        )
    except Exception as e:
        logger.error(f"LangChain en2zh translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain/summarize", response_model=SummarizeResponse)
async def langchain_summarize(
    request: SummarizeRequest,
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    使用LangChain框架进行文本总结
    支持链式调用和上下文管理
    """
    try:
        if hasattr(service, 'model_name') and request.model:
            service.model_name = request.model
        if hasattr(service, 'use_chains'):
            service.use_chains = True
            
        result = await service.summarize(
            text=request.text,
            max_length=request.max_length,
            context=request.context
        )
        return SummarizeResponse(summary=result)
    except Exception as e:
        logger.error(f"LangChain summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/langchain/chains/list")
async def list_available_chains(
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    列出可用的LangChain链
    """
    chains = service.list_available_chains()
    return {"available_chains": chains}


@router.post("/langchain/chains/inspect/{chain_name}")
async def inspect_chain(
    chain_name: str,
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    检查特定链的配置和状态
    """
    try:
        chain_info = service.inspect_chain(chain_name)
        return {"chain_name": chain_name, "chain_info": chain_info}
    except Exception as e:
        logger.error(f"Chain inspection error: {e}")
        raise HTTPException(status_code=404, detail=f"Chain '{chain_name}' not found or inspection failed")


@router.delete("/langchain/chains/clear")
async def clear_chain_memory(
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    清空链的内存/上下文
    """
    try:
        service.clear_memory()
        return {"message": "Chain memory cleared successfully"}
    except Exception as e:
        logger.error(f"Clear memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-prompt")
async def validate_prompt_type(req: ValidatePromptRequest):
    """验证提示词类型是否有效（JSON Body: { category, prompt_type }）"""
    try:
        from prompt.utils import prompt_validator
        result = prompt_validator.validate_prompt_request(req.category, req.prompt_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/zh2en", response_model=TranslateResponse)
async def translate_zh2en(
    req: SimpleTextRequest,
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    # 使用查询参数中的模型或请求体中的模型
    actual_model = getattr(req, 'model', None)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.zh2en(req.text)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="英文",
        source_language="中文",
        model=actual_model or "default"
    )


@router.post("/en2zh", response_model=TranslateResponse)
async def translate_en2zh(
    req: SimpleTextRequest,
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    actual_model = getattr(req, 'model', None)
    logger.info(actual_model)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.en2zh(req.text)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="中文",
        source_language="英文",
        model=actual_model or "default"
    )


@router.post("/auto", response_model=TranslateResponse)
async def auto_translate(
    req: SimpleTextRequest,
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """自动检测语言并翻译"""
    actual_model = getattr(req, 'model', None)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.auto_translate(req.text)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="自动检测",
        source_language="自动检测",
        model=actual_model or "default"
    )


@router.post("/summarize", response_model=TranslateResponse)
async def translate_summarize(
    req: SimpleTextRequest,
    max_length: int = Query(200, description="总结最大长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    actual_model = getattr(req, 'model', None)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.summarize(req.text, max_length=max_length)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="总结",
        source_language="原文",
        model=actual_model or "default"
    )


@router.post("/keyword-summary", response_model=TranslateResponse)
async def keyword_summary(
    req: SimpleTextRequest,
    summary_length: int = Query(100, description="总结长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """关键词提取总结"""
    actual_model = getattr(req, 'model', None)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.keyword_summary(req.text, summary_length=summary_length)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="关键词总结",
        source_language="原文",
        model=actual_model or "default"
    )


@router.post("/structured-summary", response_model=TranslateResponse)
async def structured_summary(
    req: SimpleTextRequest,
    max_length: int = Query(300, description="总结最大长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """结构化总结"""
    actual_model = getattr(req, 'model', None)
    if actual_model:
        service = TranslationService(model_name=actual_model)
    
    result = await service.structured_summary(req.text, max_length=max_length)
    return TranslateResponse(
        result=result, 
        translated_text=result,
        target_language="结构化总结",
        source_language="原文",
        model=actual_model or "default"
    )


