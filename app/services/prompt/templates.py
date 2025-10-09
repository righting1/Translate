"""
统一的提示词管理模块
"""
from enum import Enum
from typing import Dict, Any


class PromptCategory(Enum):
    """提示词类别枚举"""
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    SYSTEM = "system"


class TranslationPromptType(Enum):
    """翻译提示词类型枚举"""
    ZH_TO_EN = "ZH_TO_EN"
    EN_TO_ZH = "EN_TO_ZH"
    AUTO_TRANSLATE = "AUTO_TRANSLATE"


class SummarizationPromptType(Enum):
    """总结提示词类型枚举"""
    BASIC_SUMMARY = "BASIC_SUMMARY"
    KEYWORD_SUMMARY = "KEYWORD_SUMMARY"
    STRUCTURED_SUMMARY = "STRUCTURED_SUMMARY"


class SystemPromptType(Enum):
    """系统提示词类型枚举"""
    TRANSLATOR_ROLE = "TRANSLATOR_ROLE"
    SUMMARIZER_ROLE = "SUMMARIZER_ROLE"


class PromptTemplate:
    """提示词模板基类"""
    
    def __init__(self, template: str, variables: Dict[str, Any] = None):
        self.template = template
        self.variables = variables or {}
    
    def format(self, **kwargs) -> str:
        """格式化提示词"""
        variables = {**self.variables, **kwargs}
        return self.template.format(**variables)


class TranslationPrompts:
    """翻译相关的提示词"""
    
    # 中文翻译成英文
    ZH_TO_EN = PromptTemplate(
        template="""你是一个专业的翻译助手，请将以下中文文本翻译成英文。
要求：
1. 保持原意不变
2. 语言自然流畅
3. 符合英文表达习惯
4. 如果是专业术语，请使用准确的专业词汇
待翻译文本：
{text}
请直接返回翻译结果，不要包含其他解释。"""
    )
    
    # 英文翻译成中文
    EN_TO_ZH = PromptTemplate(
        template="""你是一个专业的翻译助手，请将以下英文文本翻译成中文。
要求：
1. 保持原意不变
2. 语言自然流畅
3. 符合中文表达习惯
4. 如果是专业术语，请使用准确的中文术语

待翻译文本：
{text}

请直接返回翻译结果，不要包含其他解释。"""
    )
    
    # 自动检测语言并翻译
    AUTO_TRANSLATE = PromptTemplate(
        template="""你是一个专业的翻译助手，请分析以下文本的语言，并进行翻译：
- 如果是中文，翻译成英文
- 如果是英文，翻译成中文
- 如果是其他语言，翻译成中文

要求：
1. 保持原意不变
2. 语言自然流畅
3. 符合目标语言表达习惯

待翻译文本：
{text}

请直接返回翻译结果，不要包含其他解释。"""
    )


class SummarizationPrompts:
    """文本总结相关的提示词"""
    
    # 基础总结
    BASIC_SUMMARY = PromptTemplate(
        template="""请对以下文本进行总结，要求：
1. 提取核心要点
2. 保持逻辑清晰
3. 长度控制在{max_length}字以内
4. 使用简洁明了的语言

原文内容：
{text}

请直接返回总结内容。"""
    )
    
    # 关键词提取总结
    KEYWORD_SUMMARY = PromptTemplate(
        template="""请对以下文本进行分析，提供：
1. 核心总结（{summary_length}字以内）
2. 关键词（3-5个）
3. 主要观点（2-3条）

原文内容：
{text}

请按以下格式返回：
总结：[总结内容]
关键词：[关键词1, 关键词2, ...]
主要观点：
- [观点1]
- [观点2]
- [观点3]"""
    )
    
    # 结构化总结
    STRUCTURED_SUMMARY = PromptTemplate(
        template="""请对以下文本进行结构化总结，按照以下结构组织：            
1. 主题概述
2. 核心内容
3. 重要细节
4. 结论要点

要求：
- 每部分都要简洁明了
- 总长度控制在{max_length}字以内
- 保持逻辑性和完整性

原文内容：
{text}

请按指定结构返回总结。"""
    )


class SystemPrompts:
    """系统级提示词"""
    
    # 系统角色设定
    TRANSLATOR_ROLE = """你是一个专业的AI翻译助手，具有以下特点：
1. 精通中英文互译
2. 了解各领域专业术语
3. 能够根据语境选择最合适的表达方式
4. 保持翻译的准确性和自然性
5. 对于不确定的内容会如实说明"""
    
    SUMMARIZER_ROLE = """你是一个专业的文本分析和总结助手，具有以下能力：
1. 快速理解文本核心内容
2. 提取关键信息和要点
3. 生成简洁明了的总结
4. 保持逻辑结构清晰
5. 根据需求调整总结风格和长度"""


# 提示词管理器
class PromptManager:
    """提示词管理器，统一管理所有提示词模板"""
    
    def __init__(self):
        self.translation = TranslationPrompts()
        self.summarization = SummarizationPrompts()
        self.system = SystemPrompts()
    
    def get_prompt(self, category: PromptCategory, prompt_name: str, **kwargs) -> str:
        """获取格式化后的提示词（使用枚举）"""
        if category == PromptCategory.TRANSLATION:
            prompt_template = getattr(self.translation, prompt_name, None)
        elif category == PromptCategory.SUMMARIZATION:
            prompt_template = getattr(self.summarization, prompt_name, None)
        elif category == PromptCategory.SYSTEM:
            return getattr(self.system, prompt_name, "")
        else:
            raise ValueError(f"Unknown category: {category}")
        
        if prompt_template is None:
            raise ValueError(f"Unknown prompt: {prompt_name}")
        
        if isinstance(prompt_template, PromptTemplate):
            return prompt_template.format(**kwargs)
        else:
            return prompt_template
    
    def get_translation_prompt(self, prompt_type: TranslationPromptType, **kwargs) -> str:
        """获取翻译提示词（类型安全）"""
        return self.get_prompt(PromptCategory.TRANSLATION, prompt_type.value, **kwargs)
    
    def get_summarization_prompt(self, prompt_type: SummarizationPromptType, **kwargs) -> str:
        """获取总结提示词（类型安全）"""
        return self.get_prompt(PromptCategory.SUMMARIZATION, prompt_type.value, **kwargs)
    
    def get_system_prompt(self, prompt_type: SystemPromptType) -> str:
        """获取系统提示词（类型安全）"""
        return self.get_prompt(PromptCategory.SYSTEM, prompt_type.value)
    
    # 保持向后兼容的方法
    def get_prompt_by_string(self, category: str, prompt_name: str, **kwargs) -> str:
        """获取格式化后的提示词（字符串方式，保持向后兼容）"""
        try:
            category_enum = PromptCategory(category)
            return self.get_prompt(category_enum, prompt_name, **kwargs)
        except ValueError:
            raise ValueError(f"Unknown category: {category}")


# 全局提示词管理器实例
prompt_manager = PromptManager()