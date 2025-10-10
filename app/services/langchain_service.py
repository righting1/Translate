# -*- coding: utf-8 -*-
"""
基于LangChain的AI模型服务
提供统一的LangChain接口和更丰富的功能
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from enum import Enum

try:
    from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
    from langchain_core.language_models.base import BaseLanguageModel
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..core.config import settings

logger = logging.getLogger(__name__)

# 如果 LangChain 不可用，记录警告
if not LANGCHAIN_AVAILABLE:
    logger.warning("LangChain not available. Using mock services.")


class LangChainModelType(Enum):
    """LangChain支持的模型类型"""
    OPENAI = "openai"
    DASHSCOPE = "dashscope" 
    ZHIPUAI = "zhipuai"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"


class BaseLangChainService:
    """LangChain服务基类"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config
        self.model_name = model_config.get("model", "default")
        self.service_type = model_config.get("service_type", "openai")
        self.llm = None  # 添加llm属性
        
        if LANGCHAIN_AVAILABLE:
            try:
                # 使用更新的内存类来避免弃用警告
                from langchain.memory import ConversationBufferMemory
                self.memory = ConversationBufferMemory(return_messages=True)
            except ImportError:
                # 如果导入失败，使用简单的内存实现
                self.memory = {"messages": []}
            
            # 尝试初始化LLM
            try:
                self._initialize_llm()
            except Exception as e:
                logger.warning(f"Failed to initialize LLM for {self.model_name}: {e}")
        else:
            self.memory = {"messages": []}
    
    def _initialize_llm(self):
        """初始化LLM实例"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, skipping LLM initialization")
            return
        
        logger.info(f"Initializing LLM for service type: {self.service_type}, model: {self.model_name}")
        logger.debug(f"Config: {self.config}")
        
        try:
            # 根据服务类型创建对应的LLM
            service_type = self.service_type.lower()
            
            if service_type in ["openai", "azure_openai"]:
                api_key = self.config.get("api_key") or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                base_url = self.config.get("base_url") or settings.openai_base_url
                if api_key:
                    logger.info(f"Creating OpenAI LLM with model: {self.config.get('model', 'gpt-3.5-turbo')}")
                    try:
                        self.llm = ChatOpenAI(
                            model=self.config.get("model", "gpt-3.5-turbo"),
                            api_key=api_key,
                            base_url=base_url,
                            temperature=self.config.get("temperature", 0.7),
                            max_tokens=self.config.get("max_tokens", 2000),
                            timeout=self.config.get("timeout", 60)
                        )
                        logger.info("OpenAI LLM created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create OpenAI LLM: {e}")
                        self.llm = None
                else:
                    logger.error("OpenAI API key not found in config or environment")
                    logger.info("Please set OPENAI_API_KEY environment variable or add api_key to config")
            elif service_type == "dashscope":
                # DashScope集成
                logger.info("Setting up DashScope LLM")
                api_key = self.config.get("api_key") or settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY")
                if api_key:
                    logger.info("DashScope API key found, creating LLM instance")
                    try:
                        # 使用正确的 DashScope 配置
                        self.llm = ChatOpenAI(
                            model=self.config.get("model", "qwen-turbo"),
                            api_key=api_key,
                            base_url=self.config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                            temperature=self.config.get("temperature", 0.7),
                            max_tokens=self.config.get("max_tokens", 2000),
                            timeout=self.config.get("timeout", 60)  # 增加超时时间
                        )
                        logger.info("DashScope LLM created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create DashScope LLM: {e}")
                        self.llm = None
                else:
                    logger.error("DashScope API key not found in config or environment")
                    logger.info("Please set DASHSCOPE_API_KEY environment variable or add api_key to config")
            elif service_type == "zhipuai":
                logger.info("ZhipuAI integration will be implemented later")
            elif service_type == "ollama":
                # Ollama本地模型
                try:
                    from langchain_community.llms import Ollama
                    logger.info(f"Creating Ollama LLM with model: {self.config.get('model', 'llama2')}")
                    self.llm = Ollama(
                        model=self.config.get("model", "llama2"),
                        base_url=self.config.get("base_url", "http://localhost:11434"),
                        temperature=self.config.get("temperature", 0.7)
                    )
                    logger.info("Ollama LLM created successfully")
                except ImportError:
                    logger.error("Ollama integration requires langchain_community")
            else:
                logger.warning(f"Service type '{service_type}' LLM not implemented")
                
            # 验证 LLM 是否成功创建
            if self.llm is not None:
                logger.info(f"LLM initialization successful: {type(self.llm).__name__}")
            else:
                logger.error("LLM initialization failed: self.llm is None")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        logger.debug(f"generate_text called with prompt length: {len(prompt)}")
        logger.debug(f"LangChain available: {LANGCHAIN_AVAILABLE}")
        logger.debug(f"self.llm is None: {self.llm is None}")
        logger.debug(f"self.llm type: {type(self.llm) if self.llm else 'None'}")
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, returning mock response")
            return f"Mock response for: {prompt[:50]}..."
            
        if self.llm is None:
            logger.error("self.llm is None, attempting to reinitialize...")
            try:
                self._initialize_llm()
                if self.llm is None:
                    logger.error("Reinitialization failed, self.llm is still None")
                    return f"LLM initialization failed for: {prompt[:50]}..."
                else:
                    logger.info("LLM reinitialization successful")
            except Exception as e:
                logger.error(f"Reinitialization error: {e}")
                return f"LLM initialization error: {str(e)}"
        
        try:
            logger.debug(f"Attempting to generate text with LLM: {type(self.llm).__name__}")
            if hasattr(self.llm, 'ainvoke'):
                logger.debug("Using ainvoke method")
                result = await self.llm.ainvoke(prompt)
                response = result.content if hasattr(result, 'content') else str(result)
                logger.info(f"Text generation successful, response length: {len(response)}")
                return response
            else:
                logger.debug("Using invoke method (sync fallback)")
                # 同步调用的回退
                result = self.llm.invoke(prompt)
                response = result.content if hasattr(result, 'content') else str(result)
                logger.info(f"Text generation successful, response length: {len(response)}")
                return response
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return f"Text generation failed: {str(e)}"

    async def generate_text_stream(self, prompt: str, **kwargs):
        """
        以流式方式生成文本，返回一个异步生成器，逐步产出内容片段。
        优先调用 llm.astream；若不可用，则回退为一次性生成并分片输出。
        """
        if LANGCHAIN_AVAILABLE and self.llm is not None and hasattr(self.llm, "astream"):
            try:
                async for chunk in self.llm.astream(prompt):
                    piece = None
                    # 兼容不同返回结构
                    if hasattr(chunk, "content") and chunk.content:
                        piece = chunk.content
                    elif hasattr(chunk, "delta") and getattr(chunk, "delta"):
                        piece = getattr(chunk, "delta")
                    elif isinstance(chunk, str):
                        piece = chunk
                    if piece:
                        yield piece
                return
            except Exception as e:
                logger.error(f"astream failed, fallback to non-stream: {e}")
        # 回退：一次性生成，再切片输出
        text = await self.generate_text(prompt, **kwargs)
        step = 32
        for i in range(0, len(text), step):
            yield text[i:i+step]
    
    async def chat_completion(self, messages, **kwargs) -> str:
        """聊天完成"""
        if not LANGCHAIN_AVAILABLE:
            return "Mock chat response"
        
        return "Chat completion response"
    
    def create_chain(self, prompt_template: str, **kwargs):
        """创建LangChain链"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        return None
    
    def create_conversation_chain(self, **kwargs):
        """创建对话链"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        return None


class LangChainManager:
    """LangChain服务管理器"""
    
    def __init__(self):
        self.services: Dict[str, BaseLangChainService] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化所有配置的服务"""
        try:
            ai_config = settings.ai_model
            
            if not ai_config:
                logger.warning("No AI model configuration found")
                return
                
            # 遍历配置中的模型，跳过非模型配置项
            excluded_keys = {"default_model"}  # 排除非模型配置
            
            for model_name, model_config in ai_config.items():
                if model_name in excluded_keys:
                    continue
                    
                # 确保 model_config 是字典类型
                if not isinstance(model_config, dict):
                    logger.warning(f"Invalid config for {model_name}: {type(model_config)}")
                    continue
                
                # 默认启用所有配置的模型
                if model_config.get("enabled", True):
                    try:
                        service = self._create_service(model_name, model_config)
                        if service:
                            self.services[model_name] = service
                    except Exception as e:
                        logger.warning(f"Failed to initialize {model_name} LangChain service: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain services: {e}")
            # 创建一个默认服务
            self.services["default"] = self._create_default_service()
    
    def _create_service(self, model_name: str, model_config: Dict[str, Any]) -> Optional[BaseLangChainService]:
        """根据模型名称和配置创建相应的服务"""
        try:
            logger.info(f"Creating service for model: {model_name}")
            logger.debug(f"Model config: {model_config}")
            
            # 使用配置中的 service_type，如果没有则使用 model_name
            service_type = model_config.get("service_type", model_name)
            
            service_config = {
                **model_config,
                "service_type": service_type  # 使用正确的服务类型
            }
            
            logger.debug(f"Final service config: {service_config}")
            logger.info(f"Creating service with type: {service_type}")
            
            service = BaseLangChainService(service_config)
            
            if service and service.llm is not None:
                logger.info(f"✓ Service created successfully for {model_name}: LLM type = {type(service.llm).__name__}")
            elif service:
                logger.warning(f"⚠ Service created for {model_name} but LLM is None")
            else:
                logger.error(f"✗ Failed to create service for {model_name}")
                
            return service
        except Exception as e:
            logger.error(f"Error creating service for {model_name}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _create_default_service(self) -> BaseLangChainService:
        """创建默认服务"""
        default_config = {
            "model": "default",
            "temperature": 0.3,
            "max_tokens": 2000,
            "timeout": 30
        }
        return BaseLangChainService(default_config)
    
    def get_service(self, model_name: Optional[str] = None) -> Optional[BaseLangChainService]:
        """获取指定的服务"""
        logger.info(f"Settings object: {settings}")
        logger.info(f"AI model config: {settings.ai_model}")
        logger.info(f"Default model: {settings.ai_model.get('default_model') if settings.ai_model else 'None'}")

        # 兼容空字符串：统一回退到 None 以使用默认模型
        if model_name is not None and isinstance(model_name, str) and model_name.strip() == "":
            model_name = None

        if model_name is None:
            try:
                model_name = settings.ai_model.get("default_model") if settings.ai_model else "default"
            except Exception as e:
                logger.warning(f"Failed to get default model: {e}")
                model_name = "default"
        
        logger.info(f"Looking for service: {model_name}")
        service = self.services.get(model_name) or self.services.get("default")
        logger.info(f"Found service: {service is not None}")
        
        return service
    
    def get_default_service(self) -> Optional[BaseLangChainService]:
        """获取默认服务"""
        return self.get_service()
    
    def get_available_services(self) -> List[str]:
        """获取可用的服务列表"""
        return list(self.services.keys())
    
    def register_service(self, name: str, service: BaseLangChainService):
        """注册自定义服务"""
        self.services[name] = service
    
    async def generate_with_fallback(self, prompt: str, preferred_models: Optional[List[str]] = None, **kwargs) -> str:
        """使用回退机制生成文本"""
        if preferred_models is None:
            preferred_models = ["default"]
        
        last_error = None
        
        for model_name in preferred_models:
            service = self.get_service(model_name)
            if service:
                try:
                    return await service.generate_text(prompt, **kwargs)
                except Exception as e:
                    last_error = e
                    continue
        
        # 尝试所有可用服务
        for service_name, service in self.services.items():
            if service_name not in preferred_models:
                try:
                    return await service.generate_text(prompt, **kwargs)
                except Exception as e:
                    last_error = e
                    continue
        
        raise Exception(f"All LangChain services failed. Last error: {last_error}")

    def create_chain(self, chain_name: str, prompt_template: str, model_name: Optional[str] = None):
        """创建LangChain链"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            service = self.get_service(model_name)
            if not service or not hasattr(service, 'llm'):
                return None
                
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            chain = LLMChain(llm=service.llm, prompt=prompt)
            
            # 存储链
            if not hasattr(self, '_chains'):
                self._chains = {}
            self._chains[chain_name] = chain
            
            return chain
        except Exception as e:
            logger.error(f"Failed to create chain {chain_name}: {e}")
            return None
    
    def get_chain(self, chain_name: str):
        """获取已创建的链"""
        if not hasattr(self, '_chains'):
            return None
        return self._chains.get(chain_name)
    
    async def run_chain(self, chain_name: str, inputs: Dict[str, Any], model_name: Optional[str] = None) -> str:
        """运行链"""
        logger.debug(f"Running chain: {chain_name} with inputs: {list(inputs.keys())}")
        
        chain = self.get_chain(chain_name)
        if chain is None:
            logger.warning(f"Chain '{chain_name}' not found, falling back to direct generation")
            # 如果链不存在，尝试直接生成
            service = self.get_service(model_name)
            if service:
                # 将输入转换为字符串提示
                prompt_text = inputs.get('text', '') if isinstance(inputs, dict) else str(inputs)
                return await service.generate_text(prompt_text)
            
            from ..utils.exceptions import ModelNotAvailableError
            raise ModelNotAvailableError(f"Chain '{chain_name}' not found and no service available")
        
        try:
            if LANGCHAIN_AVAILABLE:
                logger.debug("Using LangChain to run chain")
                
                # 使用新的 LangChain API 代替已弃用的 arun
                if hasattr(chain, 'ainvoke'):
                    logger.debug("Using ainvoke method")
                    result = await chain.ainvoke(inputs)
                elif hasattr(chain, 'arun'):
                    logger.warning("Using deprecated arun method")
                    result = await chain.arun(**inputs)
                elif hasattr(chain, 'invoke'):
                    logger.debug("Using sync invoke method")
                    result = chain.invoke(inputs)
                else:
                    logger.error("Chain has no invoke method available")
                    return f"Chain '{chain_name}' has no compatible invoke method"
                
                # 处理不同类型的返回结果
                if hasattr(result, 'content'):
                    response = result.content
                elif isinstance(result, dict):
                    response = result.get('text', str(result))
                else:
                    response = str(result)
                
                logger.info(f"Chain execution successful, response length: {len(response)}")
                return response
            else:
                logger.warning("LangChain not available, returning mock result")
                return f"Mock chain result for {chain_name}"
                
        except Exception as e:
            logger.error(f"Chain execution failed: {str(e)}")
            
            # 更详细的错误处理
            if "404" in str(e) or "Not Found" in str(e):
                logger.error("404 error detected - likely API endpoint or authentication issue")
                return f"Chain execution failed: API endpoint not found (404). Please check your API configuration and keys."
            elif "401" in str(e) or "Unauthorized" in str(e):
                logger.error("401 error detected - authentication issue")
                return f"Chain execution failed: Authentication failed (401). Please check your API keys."
            elif "timeout" in str(e).lower():
                logger.error("Timeout error detected")
                return f"Chain execution failed: Request timeout. Please try again."
            else:
                import traceback
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                return f"Chain execution failed: {str(e)}"
    
    def clear_memory(self):
        """清空所有服务的内存"""
        for service in self.services.values():
            if hasattr(service, 'memory') and service.memory:
                service.memory.clear()
    
    async def generate_text(self, prompt: str, service_name: Optional[str] = None, **kwargs) -> str:
        """直接生成文本的便捷方法"""
        service = self.get_service(service_name)
        if service:
            return await service.generate_text(prompt, **kwargs)
        
        from ..utils.exceptions import ModelNotAvailableError
        raise ModelNotAvailableError(f"No service available for text generation. Requested service: {service_name}")

    async def generate_text_stream(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        service_name: Optional[str] = None,
        **kwargs,
    ):
        """
        直接流式生成文本的便捷方法（异步生成器）。
        优先使用 model_name，其次 service_name，最后默认服务。
        """
        svc = None
        if model_name is not None:
            svc = self.get_service(model_name)
        elif service_name is not None:
            svc = self.get_service(service_name)
        else:
            svc = self.get_default_service()

        if svc and hasattr(svc, "generate_text_stream"):
            async for piece in svc.generate_text_stream(prompt, **kwargs):
                yield piece
            return

        # 回退：一次性生成，再切片输出
        text = await self.generate_text(prompt, service_name=model_name or service_name, **kwargs)
        step = 32
        for i in range(0, len(text), step):
            yield text[i:i+step]
    
    async def chat_completion(self, messages: list, service_name: Optional[str] = None, **kwargs) -> str:
        """聊天完成的便捷方法"""
        service = self.get_service(service_name)
        if service and hasattr(service, 'chat_completion'):
            return await service.chat_completion(messages, **kwargs)
        elif service:
            # 将消息转换为简单文本
            text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
            return await service.generate_text(text, **kwargs)
        
        from ..utils.exceptions import ModelNotAvailableError
        raise ModelNotAvailableError(f"No service available for chat completion. Requested service: {service_name}")


# 全局LangChain管理器实例
langchain_manager = LangChainManager()


def get_langchain_service(model_name: Optional[str] = None) -> Optional[BaseLangChainService]:
    """获取LangChain服务的便捷函数"""
    return langchain_manager.get_service(model_name)


def get_default_langchain_service() -> Optional[BaseLangChainService]:
    """获取默认LangChain服务的便捷函数"""
    return langchain_manager.get_default_service()