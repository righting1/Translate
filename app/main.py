import logging
from fastapi import FastAPI
from .api.v1.routes import router as v1_router
from .api.translate.routes import router as translate_router
from .api.async_tasks.routes import router as async_router
from .api.stream.routes import router as stream_router
from .core.config import settings
from .utils.error_handlers import register_exception_handlers
from .utils.logging_config import setup_logging, get_logger
import uvicorn

# 设置日志配置
setup_logging(
    level=settings.log_level.upper() if hasattr(settings, 'log_level') else "INFO",
    log_file="app.log"  # 日志文件保存在项目根目录
)

# 获取应用日志记录器
logger = get_logger(__name__)

# 设置特定模块的日志级别
logging.getLogger("services.langchain_service").setLevel(logging.DEBUG)
logging.getLogger("services.langchain_translate").setLevel(logging.DEBUG)

logger.info("正在初始化FastAPI应用...")
logger.info(f"应用名称: {settings.app_name}")
logger.info(f"调试模式: {settings.debug}")
logger.info(f"主机: {settings.host}:{settings.port}")

app = FastAPI(title=settings.app_name, debug=settings.debug)

# 注册全局异常处理器
register_exception_handlers(app)
logger.info("全局异常处理器已注册")

# 注册路由
app.include_router(v1_router)
logger.info("V1 API路由已注册")

app.include_router(translate_router)
logger.info("翻译API路由已注册")

app.include_router(async_router)
logger.info("异步任务路由已注册")

app.include_router(stream_router)
logger.info("流式API路由已注册")

logger.info("FastAPI应用初始化完成")


if __name__ == "__main__":
    logger.info("正在启动Uvicorn服务器...")
    logger.info(f"服务器配置: host={settings.host}, port={settings.port}, reload={settings.reload}")
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level,
        )
    except Exception as e:
        logger.error(f"启动服务器时发生错误: {e}")
        raise
