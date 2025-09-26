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
from schemas.translate import FeatureCode

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/translate", tags=["translate"])


def get_translation_service(req: TranslateRequest) -> TranslationService:
    return TranslationService(model_name=req.model)


def get_simple_translation_service(model: Optional[str] = None) -> TranslationService:
    return TranslationService(model_name=model)


def get_langchain_service(model: Optional[str] = None, use_chains: bool = True) -> LangChainTranslationService:
    return LangChainTranslationService(model_name=model, use_chains=use_chains)


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
        Feature(code=FeatureCode.zh2en, name="中译英", description="将中文翻译为英文"),
        Feature(code=FeatureCode.en2zh, name="英译中", description="将英文翻译为中文"),
        Feature(code=FeatureCode.summarize, name="总结摘要", description="对输入文本进行简要总结"),
        Feature(code=FeatureCode.auto_translate, name="自动翻译", description="自动检测语言并翻译"),
        Feature(code=FeatureCode.keyword_summary, name="关键词总结", description="提取关键词并总结"),
        Feature(code=FeatureCode.structured_summary, name="结构化总结", description="按结构化格式总结"),
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链"),
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    使用LangChain框架进行翻译
    支持链式调用和对话上下文管理
    """
    try:
        if hasattr(service, 'model_name') and model:
            service.model_name = model
        if hasattr(service, 'use_chains'):
            service.use_chains = use_chains
            
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链"),
    service: LangChainTranslationService = Depends(get_langchain_service)
) -> TranslateResponse:
    """
    使用LangChain框架将中文翻译成英文
    """
    try:
        if hasattr(service, 'model_name') and model:
            service.model_name = model
        if hasattr(service, 'use_chains'):
            service.use_chains = use_chains
            
        result = await service.zh2en(req.text)
        return TranslateResponse(
            result=result, 
            translated_text=result,
            target_language="英文",
            source_language="中文",
            model=model or "langchain_default"
        )
    except Exception as e:
        logger.error(f"LangChain zh2en translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain/en2zh", response_model=TranslateResponse)
async def langchain_translate_en2zh(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链"),
    service: LangChainTranslationService = Depends(get_langchain_service)
) -> TranslateResponse:
    """
    使用LangChain框架将英文翻译成中文
    """
    try:
        if hasattr(service, 'model_name') and model:
            service.model_name = model
        if hasattr(service, 'use_chains'):
            service.use_chains = use_chains
            
        result = await service.en2zh(req.text)
        return TranslateResponse(
            result=result, 
            translated_text=result,
            target_language="中文",
            source_language="英文",
            model=model or "langchain_default"
        )
    except Exception as e:
        logger.error(f"LangChain en2zh translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain/summarize", response_model=SummarizeResponse)
async def langchain_summarize(
    request: SummarizeRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链"),
    service: LangChainTranslationService = Depends(get_langchain_service)
):
    """
    使用LangChain框架进行文本总结
    支持链式调用和上下文管理
    """
    try:
        if hasattr(service, 'model_name') and model:
            service.model_name = model
        if hasattr(service, 'use_chains'):
            service.use_chains = use_chains
            
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
async def validate_prompt_type(category: str, prompt_type: str):
    """验证提示词类型是否有效"""
    try:
        from prompt.utils import prompt_validator
        result = prompt_validator.validate_prompt_request(category, prompt_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/zh2en", response_model=TranslateResponse)
async def translate_zh2en(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    # 使用查询参数中的模型或请求体中的模型
    actual_model = model or getattr(req, 'model', None)
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    actual_model = model or getattr(req, 'model', None)
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """自动检测语言并翻译"""
    actual_model = model or getattr(req, 'model', None)
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    max_length: int = Query(200, description="总结最大长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    actual_model = model or getattr(req, 'model', None)
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    summary_length: int = Query(100, description="总结长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """关键词提取总结"""
    actual_model = model or getattr(req, 'model', None)
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
    model: Optional[str] = Query(None, description="AI模型名称"),
    max_length: int = Query(300, description="总结最大长度"),
    service: TranslationService = Depends(get_simple_translation_service),
) -> TranslateResponse:
    """结构化总结"""
    actual_model = model or getattr(req, 'model', None)
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


# ============== 异步任务 API 端点 ==============

@router.post("/async/zh2en")
async def submit_async_zh2en_task(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链")
):
    """
    提交异步中译英任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    try:
        task_id = task_manager.create_task(
            task_type=TaskType.ZH2EN,
            input_data={"text": req.text},
            model_name=model,
            use_chains=use_chains
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit zh2en task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async/en2zh")
async def submit_async_en2zh_task(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    use_chains: bool = Query(True, description="是否使用预构建的链")
):
    """
    提交异步英译中任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    try:
        task_id = task_manager.create_task(
            task_type=TaskType.EN2ZH,
            input_data={"text": req.text},
            model_name=model,
            use_chains=use_chains
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit en2zh task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async/summarize")
async def submit_async_summarize_task(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    max_length: int = Query(200, description="总结最大长度"),
    use_chains: bool = Query(True, description="是否使用预构建的链")
):
    """
    提交异步总结任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    try:
        task_id = task_manager.create_task(
            task_type=TaskType.SUMMARIZE,
            input_data={"text": req.text, "max_length": max_length},
            model_name=model,
            use_chains=use_chains
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit summarize task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async/keyword-summary")
async def submit_async_keyword_summary_task(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    summary_length: int = Query(100, description="总结长度"),
    use_chains: bool = Query(True, description="是否使用预构建的链")
):
    """
    提交异步关键词总结任务
    """
    try:
        task_id = task_manager.create_task(
            task_type=TaskType.KEYWORD_SUMMARY,
            input_data={"text": req.text, "summary_length": summary_length},
            model_name=model,
            use_chains=use_chains
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit keyword summary task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async/structured-summary")
async def submit_async_structured_summary_task(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None, description="AI模型名称"),
    max_length: int = Query(300, description="总结最大长度"),
    use_chains: bool = Query(True, description="是否使用预构建的链")
):
    """
    提交异步结构化总结任务
    """
    try:
        task_id = task_manager.create_task(
            task_type=TaskType.STRUCTURED_SUMMARY,
            input_data={"text": req.text, "max_length": max_length},
            model_name=model,
            use_chains=use_chains
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit structured summary task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/async/status/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    用于轮询任务进度和结果
    """
    task_status = task_manager.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status


@router.get("/async/result/{task_id}")
async def get_task_result(task_id: str):
    """
    获取任务结果
    仅返回已完成任务的结果
    """
    result = task_manager.get_task_result(task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return result


@router.delete("/async/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    取消正在执行的任务
    """
    success = task_manager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
    
    return {"message": f"Task {task_id} has been cancelled"}


@router.get("/async/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="过滤任务状态 (pending, running, completed, failed, expired)"),
    limit: int = Query(50, description="返回任务数量限制")
):
    """
    列出所有任务
    支持按状态过滤
    """
    try:
        # 转换状态参数
        filter_status = None
        if status:
            try:
                filter_status = TaskStatus(status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        tasks = task_manager.list_tasks(status=filter_status)
        
        # 限制返回数量
        if limit > 0:
            tasks = tasks[:limit]
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "filtered_by": status
        }
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/async/stats")
async def get_async_stats():
    """
    获取异步任务系统统计信息
    """
    try:
        all_tasks = task_manager.list_tasks()
        
        stats = {
            "total_tasks": len(all_tasks),
            "by_status": {},
            "by_type": {},
            "system_info": {
                "max_concurrent_tasks": task_manager.max_concurrent_tasks,
                "active_tasks": len([t for t in all_tasks if t["status"] == "running"])
            }
        }
        
        # 按状态统计
        for task in all_tasks:
            status = task["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # 按类型统计
        for task in all_tasks:
            task_type = task["task_type"]
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get async stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


