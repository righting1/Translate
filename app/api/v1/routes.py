from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/health")
async def health_check() -> dict:
    logger.debug("健康检查请求")
    return {"status": "ok"}


@router.get("/greet/{name}")
async def greet(name: str) -> dict:
    logger.info(f"收到问候请求: {name}")
    return {"message": f"Hello {name}"}



