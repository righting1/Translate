import logging
from fastapi import FastAPI
from api.v1.routes import router as v1_router
from api.translate.routes import router as translate_router
from api.async_tasks.routes import router as async_router
from api.stream.routes import router as stream_router
from core.config import settings
from utils.error_handlers import register_exception_handlers
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

# 设置特定模块的日志级别
logging.getLogger("services.langchain_service").setLevel(logging.DEBUG)
logging.getLogger("services.langchain_translate").setLevel(logging.DEBUG)

app = FastAPI(title=settings.app_name, debug=settings.debug)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(v1_router)
app.include_router(translate_router)
app.include_router(async_router)
app.include_router(stream_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
