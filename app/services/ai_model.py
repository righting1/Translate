"""
AI模型服务基类和具体实现
"""
import asyncio
import httpx
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..core.config import settings
from ..utils.exceptions import (
    AuthenticationError,
    ModelAPIError,
    NetworkError,
    TimeoutError as CustomTimeoutError,
    RateLimitError,
    ModelNotAvailableError
)

logger = logging.getLogger(__name__)


class AIModelBase(ABC):
    """AI模型服务基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """聊天补全接口"""
        pass
    
    @abstractmethod
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """文本补全接口"""
        pass


class OpenAIService(AIModelBase):
    """OpenAI模型服务"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.timeout = config.get("timeout", 30)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """OpenAI聊天补全"""
        if not self.api_key:
            raise AuthenticationError("OpenAI API key not configured", model_name=self.model)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.TimeoutException as e:
            logger.error(f"OpenAI API timeout: {e}")
            raise CustomTimeoutError(f"Request to OpenAI timed out after {self.timeout}s", self.timeout)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid OpenAI API key", model_name=self.model)
            elif e.response.status_code == 429:
                raise RateLimitError("OpenAI rate limit exceeded", model_name=self.model)
            else:
                logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
                raise ModelAPIError(f"OpenAI API error: {e.response.status_code}", self.model, e)
        except httpx.NetworkError as e:
            logger.error(f"Network error calling OpenAI: {e}")
            raise NetworkError("Failed to connect to OpenAI API", e)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Invalid response format from OpenAI: {e}")
            raise ModelAPIError("Invalid response format from OpenAI", self.model, e)
    
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """文本补全（通过聊天接口实现）"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, **kwargs)


class ZhipuAIService(AIModelBase):
    """智谱AI模型服务"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "glm-4")
        self.timeout = config.get("timeout", 30)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """智谱AI聊天补全"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """文本补全（通过聊天接口实现）"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, **kwargs)


class OllamaService(AIModelBase):
    """Ollama本地模型服务"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama2")
        self.timeout = config.get("timeout", 60)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Ollama聊天接口"""
        # 将消息转换为单个prompt（Ollama可能需要不同格式）
        prompt = self._messages_to_prompt(messages)
        return await self.text_completion(prompt, **kwargs)
    
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """Ollama文本生成"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3))
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["response"]
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表转换为单个prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts) + "\nAssistant: "


class AzureOpenAIService(AIModelBase):
    """Azure OpenAI模型服务"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        self.api_version = config.get("api_version", "2024-02-01")
        self.deployment_name = config.get("deployment_name")
        self.timeout = config.get("timeout", 30)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Azure OpenAI聊天补全"""
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        }
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
        params = {"api-version": self.api_version}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """文本补全（通过聊天接口实现）"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, **kwargs)


class DashScopeService(AIModelBase):
    """阿里云DashScope模型服务（通义千问）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://dashscope.aliyuncs.com/api/v1")
        self.model = config.get("model", "qwen-plus")
        self.timeout = config.get("timeout", 30)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """DashScope聊天补全
        自动适配：
        - OpenAI 兼容模式（base_url 包含 compatible-mode）：/chat/completions
        - 原生 DashScope 接口：/services/aigc/text-generation/generation
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 判断是否为兼容模式
        is_compatible_mode = "compatible-mode" in (self.base_url or "")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if is_compatible_mode:
                # OpenAI 兼容模式
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3)),
                    "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
                }
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                # 原生 DashScope 接口
                data = {
                    "model": self.model,
                    "input": {
                        "messages": messages
                    },
                    "parameters": {
                        "temperature": kwargs.get("temperature", self.config.get("temperature", 0.3)),
                        "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
                    }
                }
                response = await client.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                # DashScope 原生响应格式
                if "output" in result and "text" in result["output"]:
                    return result["output"]["text"]
                else:
                    raise ValueError(f"Unexpected response format: {result}")
    
    async def text_completion(self, prompt: str, **kwargs) -> str:
        """文本补全（通过聊天接口实现）"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, **kwargs)


class AIModelFactory:
    """AI模型工厂类"""
    
    _services = {
        # "openai": OpenAIService,
        # "zhipuai": ZhipuAIService,
        # "ollama": OllamaService,
        # "azure_openai": AzureOpenAIService,
        "dashscope": DashScopeService
    }
    
    @classmethod
    def create_service(cls, model_type: str, config: Dict[str, Any]) -> AIModelBase:
        """创建AI模型服务实例"""
        if model_type not in cls._services:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        service_class = cls._services[model_type]
        return service_class(config)
    
    @classmethod
    def get_available_services(cls) -> List[str]:
        """获取支持的服务类型列表"""
        return list(cls._services.keys())


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self._services: Dict[str, AIModelBase] = {}
        self._default_service: Optional[str] = None
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化所有配置的服务"""
        ai_config = getattr(settings, 'ai_model', {})
        self._default_service = ai_config.get('default_model', 'openai')
        
        for service_name in AIModelFactory.get_available_services():
            service_config = ai_config.get(service_name)
            if service_config:
                try:
                    service = AIModelFactory.create_service(service_name, service_config)
                    self._services[service_name] = service
                except Exception as e:
                    print(f"Failed to initialize {service_name} service: {e}")
    
    def get_service(self, service_name: Optional[str] = None) -> AIModelBase:
        """获取AI服务实例"""
        # 优先使用传入的 service_name
        name = service_name or self._default_service
        # 若默认未配置或不可用，回退到首个可用服务
        if not name or name not in self._services:
            name = next(iter(self._services.keys()), None)
        if not name:
            raise ValueError("No AI services initialized")
        return self._services[name]
    
    def get_available_services(self) -> List[str]:
        """获取可用的服务列表"""
        return list(self._services.keys())
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        service_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """聊天补全（使用指定服务或默认服务）"""
        service = self.get_service(service_name)
        return await service.chat_completion(messages, **kwargs)
    
    async def text_completion(
        self, 
        prompt: str, 
        service_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """文本补全（使用指定服务或默认服务）"""
        service = self.get_service(service_name)
        return await service.text_completion(prompt, **kwargs)


# 全局AI模型管理器实例
ai_model_manager = AIModelManager()