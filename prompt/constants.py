"""
提示词常量定义
集中管理所有提示词名称，避免硬编码字符串
"""
from prompt.templates import TranslationPromptType, SummarizationPromptType, SystemPromptType


class PromptConstants:
    """提示词常量类"""
    
    # 翻译相关
    class Translation:
        ZH_TO_EN = TranslationPromptType.ZH_TO_EN.value
        EN_TO_ZH = TranslationPromptType.EN_TO_ZH.value
        AUTO_TRANSLATE = TranslationPromptType.AUTO_TRANSLATE.value
    
    # 总结相关
    class Summarization:
        BASIC_SUMMARY = SummarizationPromptType.BASIC_SUMMARY.value
        KEYWORD_SUMMARY = SummarizationPromptType.KEYWORD_SUMMARY.value
        STRUCTURED_SUMMARY = SummarizationPromptType.STRUCTURED_SUMMARY.value
    
    # 系统相关
    class System:
        TRANSLATOR_ROLE = SystemPromptType.TRANSLATOR_ROLE.value
        SUMMARIZER_ROLE = SystemPromptType.SUMMARIZER_ROLE.value


# 创建常量实例供外部使用
PROMPTS = PromptConstants()