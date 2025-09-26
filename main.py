import logging
from fastapi import FastAPI
from api.v1.routes import router as v1_router
from api.translate.routes import router as translate_router
from core.config import settings
import uvicorn

# ������־
logging.basicConfig(
    level=logging.INFO,  # ������־����
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # ���������̨
    ]
)

# �����ض�ģ�����־����
logging.getLogger("services.langchain_service").setLevel(logging.DEBUG)
logging.getLogger("services.langchain_translate").setLevel(logging.DEBUG)

app = FastAPI(title=settings.app_name, debug=settings.debug)


app.include_router(v1_router)
app.include_router(translate_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
