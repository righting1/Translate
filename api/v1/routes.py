from fastapi import APIRouter


router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@router.get("/greet/{name}")
async def greet(name: str) -> dict:
    return {"message": f"Hello {name}"}



