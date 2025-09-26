"""
提示词工具类
提供便捷的提示词操作和管理功能
"""
from typing import List, Dict, Any, Optional
from prompt.templates import (
    PromptManager, 
    PromptCategory, 
    TranslationPromptType, 
    SummarizationPromptType, 
    SystemPromptType,
    prompt_manager
)


class PromptHelper:
    """提示词辅助工具类"""
    
    def __init__(self, manager: Optional[PromptManager] = None):
        self.manager = manager or prompt_manager
    
    def get_all_translation_types(self) -> List[TranslationPromptType]:
        """获取所有翻译提示词类型"""
        return list(TranslationPromptType)
    
    def get_all_summarization_types(self) -> List[SummarizationPromptType]:
        """获取所有总结提示词类型"""
        return list(SummarizationPromptType)
    
    def get_all_system_types(self) -> List[SystemPromptType]:
        """获取所有系统提示词类型"""
        return list(SystemPromptType)
    
    def get_prompt_type_info(self) -> Dict[str, List[str]]:
        """获取所有提示词类型信息"""
        return {
            "translation": [pt.value for pt in self.get_all_translation_types()],
            "summarization": [pt.value for pt in self.get_all_summarization_types()],
            "system": [pt.value for pt in self.get_all_system_types()]
        }
    
    def validate_prompt_exists(self, category: PromptCategory, prompt_type: str) -> bool:
        """验证提示词是否存在"""
        try:
            if category == PromptCategory.TRANSLATION:
                TranslationPromptType(prompt_type)
            elif category == PromptCategory.SUMMARIZATION:
                SummarizationPromptType(prompt_type)
            elif category == PromptCategory.SYSTEM:
                SystemPromptType(prompt_type)
            return True
        except ValueError:
            return False
    
    def get_prompt_safely(self, category: str, prompt_name: str, **kwargs) -> Optional[str]:
        """安全地获取提示词，如果不存在返回None而不是抛异常"""
        try:
            return self.manager.get_prompt_by_string(category, prompt_name, **kwargs)
        except ValueError:
            return None
    
    def get_translation_prompt_safely(self, prompt_type_str: str, **kwargs) -> Optional[str]:
        """根据字符串安全地获取翻译提示词"""
        try:
            prompt_type = TranslationPromptType(prompt_type_str)
            return self.manager.get_translation_prompt(prompt_type, **kwargs)
        except ValueError:
            return None
    
    def get_summarization_prompt_safely(self, prompt_type_str: str, **kwargs) -> Optional[str]:
        """根据字符串安全地获取总结提示词"""
        try:
            prompt_type = SummarizationPromptType(prompt_type_str)
            return self.manager.get_summarization_prompt(prompt_type, **kwargs)
        except ValueError:
            return None
    
    def get_system_prompt_safely(self, prompt_type_str: str) -> Optional[str]:
        """根据字符串安全地获取系统提示词"""
        try:
            prompt_type = SystemPromptType(prompt_type_str)
            return self.manager.get_system_prompt(prompt_type)
        except ValueError:
            return None


class PromptValidator:
    """提示词验证器"""
    
    @staticmethod
    def validate_translation_prompt_type(prompt_type: str) -> bool:
        """验证翻译提示词类型"""
        try:
            TranslationPromptType(prompt_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_summarization_prompt_type(prompt_type: str) -> bool:
        """验证总结提示词类型"""
        try:
            SummarizationPromptType(prompt_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_system_prompt_type(prompt_type: str) -> bool:
        """验证系统提示词类型"""
        try:
            SystemPromptType(prompt_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_category(category: str) -> bool:
        """验证提示词类别"""
        try:
            PromptCategory(category)
            return True
        except ValueError:
            return False
    
    @classmethod
    def validate_prompt_request(cls, category: str, prompt_type: str) -> Dict[str, Any]:
        """验证提示词请求"""
        result = {
            "valid": False,
            "category_valid": cls.validate_category(category),
            "prompt_type_valid": False,
            "error_message": ""
        }
        
        if not result["category_valid"]:
            result["error_message"] = f"Invalid category: {category}"
            return result
        
        # 根据类别验证提示词类型
        if category == PromptCategory.TRANSLATION.value:
            result["prompt_type_valid"] = cls.validate_translation_prompt_type(prompt_type)
        elif category == PromptCategory.SUMMARIZATION.value:
            result["prompt_type_valid"] = cls.validate_summarization_prompt_type(prompt_type)
        elif category == PromptCategory.SYSTEM.value:
            result["prompt_type_valid"] = cls.validate_system_prompt_type(prompt_type)
        
        if not result["prompt_type_valid"]:
            result["error_message"] = f"Invalid prompt type '{prompt_type}' for category '{category}'"
            return result
        
        result["valid"] = True
        return result


# 创建全局实例
prompt_helper = PromptHelper()
prompt_validator = PromptValidator()