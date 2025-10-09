from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, AsyncGenerator
import logging

from ...schemas.translate import SimpleTextRequest
from ...services.langchain_translate import LangChainTranslationService
from ...services.prompt.templates import (
    TranslationPromptType,
    SummarizationPromptType,
    prompt_manager,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/translate/stream", tags=["streaming"])


async def _text_stream(gen: AsyncGenerator[str, None]):
    """将异步文本片段按 SSE 文本流（text/event-stream）输出，带断连保护。"""
    try:
        async for piece in gen:
            # 简单 SSE 格式：每条消息一行，以 data: 开头
            yield f"data: {piece}\n\n"
        # 结束事件（可被前端识别）
        yield "event: end\ndata: [DONE]\n\n"
    except Exception as e:
        # 客户端断开或网络异常
        logger.warning(f"SSE stream closed or failed: {e}")


def _service(model: Optional[str]) -> LangChainTranslationService:
    svc = LangChainTranslationService(model_name=model, use_chains=True)
    return svc


@router.post("/zh2en")
async def stream_zh2en(req: SimpleTextRequest, model: Optional[str] = Query(None)):
    try:
        svc = _service(model or getattr(req, 'model', None))
        # 使用与非流式一致的提示词模板，确保真正执行“中译英”
        prompt = prompt_manager.get_translation_prompt(
            TranslationPromptType.ZH_TO_EN,
            text=req.text,
        )

        async def gen():
            async for piece in svc.langchain_manager.generate_text_stream(prompt, model_name=svc.model_name):
                yield piece

        return StreamingResponse(_text_stream(gen()), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"stream zh2en error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/en2zh")
async def stream_en2zh(req: SimpleTextRequest, model: Optional[str] = Query(None)):
    try:
        svc = _service(model or getattr(req, 'model', None))
        # 使用与非流式一致的提示词模板，确保真正执行“英译中”
        prompt = prompt_manager.get_translation_prompt(
            TranslationPromptType.EN_TO_ZH,
            text=req.text,
        )

        async def gen():
            async for piece in svc.langchain_manager.generate_text_stream(prompt, model_name=svc.model_name):
                yield piece

        return StreamingResponse(_text_stream(gen()), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"stream en2zh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def stream_summarize(
    req: SimpleTextRequest,
    model: Optional[str] = Query(None),
    max_length: int = Query(200),
):
    try:
        svc = _service(model or getattr(req, 'model', None))
        # 与非流式一致的“总结”模板，避免原文回显
        prompt = prompt_manager.get_summarization_prompt(
            SummarizationPromptType.BASIC_SUMMARY,
            text=req.text,
            max_length=max_length,
        )

        async def gen():
            async for piece in svc.langchain_manager.generate_text_stream(prompt, model_name=svc.model_name):
                yield piece

        return StreamingResponse(_text_stream(gen()), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"stream summarize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
