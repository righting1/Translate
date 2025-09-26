#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于LangChain的翻译和总结服务
"""
from logging import Logger
from typing import Optional, Dict, Any
from prompt.templates import (
    TranslationPromptType, 
    SummarizationPromptType, 
    prompt_manager
)
from services.langchain_service import LangChainManager


class LangChainTranslationService:
    """基于LangChain的翻译服务"""
    
    def __init__(self, model_name: Optional[str] = None, use_chains: bool = True) -> None:
        self.model_name = model_name
        self.use_chains = use_chains
        self.langchain_manager = LangChainManager()
        self.prompt_manager = prompt_manager
        
        # 预创建常用的链
        if use_chains:
            self._initialize_chains()
    
    def _initialize_chains(self):
        """初始化常用的LangChain链"""
        try:
            # 创建翻译链
            zh_en_template = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.ZH_TO_EN, 
                text="{text}"
            )
            self.langchain_manager.create_chain(
                "zh_to_en_chain", 
                zh_en_template, 
                self.model_name
            )
            
            en_zh_template = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.EN_TO_ZH, 
                text="{text}"
            )
            self.langchain_manager.create_chain(
                "en_to_zh_chain", 
                en_zh_template, 
                self.model_name
            )
            
            auto_translate_template = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.AUTO_TRANSLATE, 
                text="{text}"
            )
            self.langchain_manager.create_chain(
                "auto_translate_chain", 
                auto_translate_template, 
                self.model_name
            )
            
            # 创建总结链
            basic_summary_template = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.BASIC_SUMMARY,
                text="{text}",
                max_length="{max_length}"
            )
            self.langchain_manager.create_chain(
                "basic_summary_chain", 
                basic_summary_template, 
                self.model_name
            )
            
            keyword_summary_template = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.KEYWORD_SUMMARY,
                text="{text}",
                summary_length="{summary_length}"
            )
            self.langchain_manager.create_chain(
                "keyword_summary_chain", 
                keyword_summary_template, 
                self.model_name
            )
            
            structured_summary_template = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.STRUCTURED_SUMMARY,
                text="{text}",
                max_length="{max_length}"
            )
            self.langchain_manager.create_chain(
                "structured_summary_chain", 
                structured_summary_template, 
                self.model_name
            )
            
        except Exception as e:
            print(f"Warning: Failed to initialize some chains: {e}")
    
    async def translate(self, text: str, target_language: str, source_language: Optional[str] = None, context: Optional[str] = None, **kwargs) -> str:
        """
        通用翻译方法，根据目标语言自动选择合适的翻译方法
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言（可选）
            context: 上下文信息（可选）
            
        Returns:
            翻译结果
        """
        try:
            # 根据目标语言选择合适的翻译方法
            if target_language in ["中文", "中", "zh", "chinese"]:
                return await self.en2zh(text, context=context, **kwargs)
            elif target_language in ["英文", "英", "en", "english"]:
                return await self.zh2en(text, context=context, **kwargs)
            else:
                # 使用自动翻译方法
                return await self.auto_translate(
                    text, 
                    target_language=target_language, 
                    source_language=source_language,
                    context=context, 
                    **kwargs
                )
        except Exception as e:
            print(f"Translation error: {e}")
            # 降级到简单翻译
            return f"Translation failed: {str(e)}"
    
    async def zh2en(self, text: str, context: Optional[str] = None, **kwargs) -> str:
        """中文翻译成英文"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("zh_to_en_chain"):
                # 使用预创建的链
                chain_inputs = {"text": text}
                if context:
                    chain_inputs["context"] = context
                    
                result = await self.langchain_manager.run_chain(
                    "zh_to_en_chain",
                    chain_inputs,
                    self.model_name
                )
            else:
                # 直接调用LangChain服务
                prompt = self.prompt_manager.get_translation_prompt(
                    TranslationPromptType.ZH_TO_EN,
                    text=text
                )
                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Translation failed: {str(e)}"
    
    async def en2zh(self, text: str, context: Optional[str] = None, **kwargs) -> str:
        """英文翻译成中文"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("en_to_zh_chain"):
                chain_inputs = {"text": text}
                if context:
                    chain_inputs["context"] = context


                result = await self.langchain_manager.run_chain(
                    "en_to_zh_chain",
                    chain_inputs,
                    self.model_name
                )
            else:
                prompt = self.prompt_manager.get_translation_prompt(
                    TranslationPromptType.EN_TO_ZH,
                    text=text
                )

                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Translation failed: {str(e)}"
    
    async def auto_translate(self, text: str, target_language: Optional[str] = None, source_language: Optional[str] = None, context: Optional[str] = None, **kwargs) -> str:
        """自动检测语言并翻译"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("auto_translate_chain"):
                chain_inputs = {"text": text}
                if target_language:
                    chain_inputs["target_language"] = target_language
                if source_language:
                    chain_inputs["source_language"] = source_language
                if context:
                    chain_inputs["context"] = context
                    
                result = await self.langchain_manager.run_chain(
                    "auto_translate_chain",
                    chain_inputs,
                    self.model_name
                )
            else:
                # 构建带有目标语言信息的提示词
                if target_language:
                    prompt = f"请将以下文本翻译成{target_language}:\n{text}"
                    if context:
                        prompt = f"请将以下文本翻译成{target_language}，上下文信息: {context}\n文本: {text}"
                else:
                    prompt = self.prompt_manager.get_translation_prompt(
                        TranslationPromptType.AUTO_TRANSLATE,
                        text=text
                    )
                
                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Translation failed: {str(e)}"
    
    async def summarize(self, text: str, max_length: int = 200, context: Optional[str] = None, **kwargs) -> str:
        """文本总结"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("basic_summary_chain"):
                chain_inputs = {"text": text, "max_length": max_length}
                if context:
                    chain_inputs["context"] = context
                    
                result = await self.langchain_manager.run_chain(
                    "basic_summary_chain",
                    chain_inputs,
                    self.model_name
                )
            else:
                if context:
                    prompt = f"请总结以下文本（最多{max_length}字），上下文信息: {context}\n文本: {text}"
                else:
                    prompt = self.prompt_manager.get_summarization_prompt(
                        SummarizationPromptType.BASIC_SUMMARY,
                        text=text,
                        max_length=max_length
                    )
                    
                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Summarization failed: {str(e)}"
    
    async def keyword_summary(self, text: str, summary_length: int = 100, **kwargs) -> str:
        """关键词提取总结"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("keyword_summary_chain"):
                result = await self.langchain_manager.run_chain(
                    "keyword_summary_chain",
                    {"text": text, "summary_length": summary_length},
                    self.model_name
                )
            else:
                prompt = self.prompt_manager.get_summarization_prompt(
                    SummarizationPromptType.KEYWORD_SUMMARY,
                    text=text,
                    summary_length=summary_length
                )
                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Keyword summary failed: {str(e)}"
    
    async def structured_summary(self, text: str, max_length: int = 300, **kwargs) -> str:
        """结构化总结"""
        try:
            if self.use_chains and self.langchain_manager.get_chain("structured_summary_chain"):
                result = await self.langchain_manager.run_chain(
                    "structured_summary_chain",
                    {"text": text, "max_length": max_length},
                    self.model_name
                )
            else:
                prompt = self.prompt_manager.get_summarization_prompt(
                    SummarizationPromptType.STRUCTURED_SUMMARY,
                    text=text,
                    max_length=max_length
                )
                result = await self.langchain_manager.generate_text(
                    prompt, 
                    service_name=self.model_name,
                    **kwargs
                )
            
            return result.strip()
            
        except Exception as e:
            return f"Structured summary failed: {str(e)}"
    
    async def chat_with_context(
        self, 
        messages: list, 
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """带上下文的对话功能（LangChain特有）"""
        try:
            # 如果提供了上下文，添加到消息开头
            if context:
                messages.insert(0, {"role": "system", "content": context})
            
            result = await self.langchain_manager.chat_completion(
                messages, 
                service_name=self.model_name,
                **kwargs
            )
            
            return result.strip()
            
        except Exception as e:
            return f"Chat completion failed: {str(e)}"
    
    def get_available_models(self) -> list:
        """获取可用的AI模型列表"""
        return self.langchain_manager.get_available_services()
    
    def list_available_chains(self) -> list:
        """列出可用的LangChain链"""
        chain_names = [
            "zh_to_en_chain", "en_to_zh_chain", "auto_translate_chain",
            "basic_summary_chain", "keyword_summary_chain", "structured_summary_chain"
        ]
        
        available_chains = []
        for name in chain_names:
            chain = self.langchain_manager.get_chain(name)
            if chain is not None:
                available_chains.append({
                    "name": name,
                    "type": type(chain).__name__,
                    "description": self._get_chain_description(name)
                })
        
        return available_chains
    
    def _get_chain_description(self, chain_name: str) -> str:
        """获取链的描述"""
        descriptions = {
            "zh_to_en_chain": "中文到英文翻译链",
            "en_to_zh_chain": "英文到中文翻译链", 
            "auto_translate_chain": "自动检测语言翻译链",
            "basic_summary_chain": "基础文本总结链",
            "keyword_summary_chain": "关键词提取总结链",
            "structured_summary_chain": "结构化总结链"
        }
        return descriptions.get(chain_name, "未知链类型")
    
    def inspect_chain(self, chain_name: str) -> Dict[str, Any]:
        """检查特定链的配置和状态"""
        chain = self.langchain_manager.get_chain(chain_name)
        if chain is None:
            raise ValueError(f"Chain '{chain_name}' not found")
        
        return {
            "name": chain_name,
            "type": type(chain).__name__,
            "description": self._get_chain_description(chain_name),
            "exists": True,
            "model_name": self.model_name,
            "use_chains": self.use_chains
        }
    
    def clear_memory(self):
        """清空链的内存/上下文"""
        try:
            # 清空LangChain管理器中的对话历史
            if hasattr(self.langchain_manager, 'clear_memory'):
                self.langchain_manager.clear_memory()
            
            # 重新初始化链
            if self.use_chains:
                self._initialize_chains()
                
        except Exception as e:
            raise RuntimeError(f"Failed to clear memory: {str(e)}")
    
    def get_chain_info(self) -> Dict[str, Any]:
        """获取已创建的链信息"""
        chains = {}
        chain_names = [
            "zh_to_en_chain", "en_to_zh_chain", "auto_translate_chain",
            "basic_summary_chain", "keyword_summary_chain", "structured_summary_chain"
        ]
        
        for name in chain_names:
            chain = self.langchain_manager.get_chain(name)
            chains[name] = {
                "exists": chain is not None,
                "type": type(chain).__name__ if chain else None
            }
        
        return {
            "use_chains": self.use_chains,
            "model_name": self.model_name,
            "available_models": self.get_available_models(),
            "chains": chains
        }