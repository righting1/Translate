from typing import Optional, Dict, Any
# 延迟导入以避免循环导入问题
# from services.ai_model import ai_model_manager  
# from prompt.templates import prompt_manager


class TranslationService:
    def __init__(self, model_name: Optional[str] = None) -> None:
        self.model_name = model_name
        # 延迟导入以避免循环导入
        self._ai_manager = None
        self._prompt_manager = None
    
    @property
    def ai_manager(self):
        if self._ai_manager is None:
            from services.ai_model import ai_model_manager
            self._ai_manager = ai_model_manager
        return self._ai_manager
    
    @property
    def prompt_manager(self):
        if self._prompt_manager is None:
            from prompt.templates import prompt_manager
            self._prompt_manager = prompt_manager
        return self._prompt_manager

    async def zh2en(self, text: str, **kwargs) -> str:
        """中文翻译成英文"""
        try:
            from prompt.templates import TranslationPromptType
            # 获取翻译提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.ZH_TO_EN,
                text=text
            )
            
            # 调用AI模型进行翻译
            result = await self.ai_manager.text_completion(
                prompt, 
                service_name=self.model_name,
                **kwargs
            )
            
            return result.strip()
            
        except Exception as e:
            # 如果AI调用失败，返回错误信息或降级处理
            return f"Translation failed: {str(e)}"

    async def en2zh(self, text: str, **kwargs) -> str:
        """英文翻译成中文"""
        try:
            from prompt.templates import TranslationPromptType
            # 获取翻译提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.EN_TO_ZH,
                text=text
            )
            
            # 调用AI模型进行翻译
            result = await self.ai_manager.text_completion(
                prompt, 
                service_name=self.model_name,
                **kwargs
            )
            
            return result.strip()
            
        except Exception as e:
            return f"Translation failed: {str(e)}"

    async def auto_translate(self, text: str, **kwargs) -> str:
        """自动检测语言并翻译"""
        try:
            from prompt.templates import TranslationPromptType
            # 获取自动翻译提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_translation_prompt(
                TranslationPromptType.AUTO_TRANSLATE,
                text=text
            )
            
            # 调用AI模型进行翻译
            result = await self.ai_manager.text_completion(
                prompt, 
                service_name=self.model_name,
                **kwargs
            )
            
            return result.strip()
            
        except Exception as e:
            return f"Translation failed: {str(e)}"

    async def summarize(self, text: str, max_length: int = 200, **kwargs) -> str:
        """文本总结"""
        try:
            from prompt.templates import SummarizationPromptType
            # 获取总结提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.BASIC_SUMMARY,
                text=text,
                max_length=max_length
            )
            
            # 调用AI模型进行总结
            result = await self.ai_manager.text_completion(
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
            from prompt.templates import SummarizationPromptType
            # 获取关键词总结提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.KEYWORD_SUMMARY,
                text=text,
                summary_length=summary_length
            )
            
            # 调用AI模型进行总结
            result = await self.ai_manager.text_completion(
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
            from prompt.templates import SummarizationPromptType
            # 获取结构化总结提示词（使用枚举类型安全）
            prompt = self.prompt_manager.get_summarization_prompt(
                SummarizationPromptType.STRUCTURED_SUMMARY,
                text=text,
                max_length=max_length
            )
            
            # 调用AI模型进行总结
            result = await self.ai_manager.text_completion(
                prompt, 
                service_name=self.model_name,
                **kwargs
            )
            
            return result.strip()
            
        except Exception as e:
            return f"Structured summary failed: {str(e)}"
    
    def get_available_models(self) -> list:
        """获取可用的AI模型列表"""
        return self.ai_manager.get_available_services()



