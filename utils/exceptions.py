"""
自定义异常类型
用于更精确的错误处理和用户友好的错误消息
"""
from typing import Optional


class TranslateAPIException(Exception):
    """API基础异常类"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AIModelException(TranslateAPIException):
    """AI模型相关异常"""
    def __init__(self, message: str, model_name: Optional[str] = None, status_code: int = 500):
        super().__init__(message, status_code)
        self.model_name = model_name
        if model_name:
            self.details["model"] = model_name


class ModelNotAvailableError(AIModelException):
    """模型不可用"""
    def __init__(self, model_name: str):
        super().__init__(
            f"Model '{model_name}' is not available or not configured",
            model_name=model_name,
            status_code=503
        )


class ModelAPIError(AIModelException):
    """模型API调用错误"""
    def __init__(self, message: str, model_name: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message, model_name, status_code=502)
        if original_error:
            self.details["original_error"] = str(original_error)
            self.details["error_type"] = type(original_error).__name__


class AuthenticationError(AIModelException):
    """认证错误（API密钥无效等）"""
    def __init__(self, message: str = "Authentication failed. Please check your API key", model_name: Optional[str] = None):
        super().__init__(message, model_name, status_code=401)


class RateLimitError(AIModelException):
    """速率限制错误"""
    def __init__(self, message: str = "Rate limit exceeded", model_name: Optional[str] = None):
        super().__init__(message, model_name, status_code=429)


class InvalidRequestError(TranslateAPIException):
    """无效请求错误"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, status_code=400)
        if field:
            self.details["field"] = field


class TextTooLongError(InvalidRequestError):
    """文本过长错误"""
    def __init__(self, length: int, max_length: int):
        super().__init__(
            f"Text too long: {length} characters (max: {max_length})",
        )
        self.details["length"] = length
        self.details["max_length"] = max_length


class EmptyTextError(InvalidRequestError):
    """空文本错误"""
    def __init__(self):
        super().__init__("Text cannot be empty")


class TaskNotFoundException(TranslateAPIException):
    """任务未找到"""
    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' not found", status_code=404)
        self.details["task_id"] = task_id


class TaskAlreadyCompletedError(TranslateAPIException):
    """任务已完成，无法取消"""
    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' is already completed", status_code=409)
        self.details["task_id"] = task_id


class ConfigurationError(TranslateAPIException):
    """配置错误"""
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, status_code=500)
        if config_key:
            self.details["config_key"] = config_key


class LangChainError(TranslateAPIException):
    """LangChain相关错误"""
    def __init__(self, message: str, chain_name: Optional[str] = None):
        super().__init__(message, status_code=500)
        if chain_name:
            self.details["chain"] = chain_name


class ChainNotFoundError(LangChainError):
    """链未找到"""
    def __init__(self, chain_name: str):
        super().__init__(f"Chain '{chain_name}' not found", chain_name=chain_name)
        self.status_code = 404


class NetworkError(TranslateAPIException):
    """网络错误"""
    def __init__(self, message: str = "Network error occurred", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503)
        if original_error:
            self.details["original_error"] = str(original_error)


class TimeoutError(NetworkError):
    """超时错误"""
    def __init__(self, message: str = "Request timeout", timeout_seconds: Optional[int] = None):
        super().__init__(message)
        self.status_code = 504
        if timeout_seconds:
            self.details["timeout"] = timeout_seconds
