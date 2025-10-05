"""
全局异常处理器
统一处理API异常并返回标准化的错误响应
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union
from utils.exceptions import TranslateAPIException

logger = logging.getLogger(__name__)


async def translate_api_exception_handler(request: Request, exc: TranslateAPIException) -> JSONResponse:
    """处理自定义API异常"""
    logger.error(
        f"API Exception: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} errors",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "status_code": 422,
            "details": {"validation_errors": errors},
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    logger.error(
        f"HTTP Exception: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "details": {},
            "path": request.url.path
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未预期的异常（最后的防线）"""
    logger.exception(
        "Unexpected error occurred",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        },
        exc_info=exc
    )
    
    # 生产环境不暴露详细错误信息
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "details": {"error_type": type(exc).__name__},
            "path": request.url.path
        }
    )


def register_exception_handlers(app):
    """注册所有异常处理器到FastAPI应用"""
    from fastapi.exceptions import RequestValidationError
    from utils.exceptions import TranslateAPIException
    
    app.add_exception_handler(TranslateAPIException, translate_api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")
