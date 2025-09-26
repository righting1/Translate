#!/usr/bin/env python3
"""
AI大模型集成测试脚本
用于测试配置和基本功能
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from services.ai_model import ai_model_manager
from services.translate import TranslationService
from prompt.templates import prompt_manager


async def test_config():
    """测试配置加载"""
    print("=== 配置测试 ===")
    print(f"应用名称: {settings.app_name}")
    print(f"AI模型配置: {settings.ai_model is not None}")
    
    if settings.ai_model:
        print(f"默认模型: {settings.ai_model.get('default_model', 'None')}")
        print(f"配置的模型服务: {list(settings.ai_model.keys())}")
    
    print()


async def test_prompt_manager():
    """测试提示词管理器"""
    print("=== 提示词管理器测试 ===")
    
    try:
        # 测试翻译提示词
        zh_en_prompt = prompt_manager.get_prompt(
            "translation", 
            "ZH_TO_EN", 
            text="你好，世界！"
        )
        print("中译英提示词模板加载成功")
        print(f"示例长度: {len(zh_en_prompt)} 字符")
        
        # 测试总结提示词
        summary_prompt = prompt_manager.get_prompt(
            "summarization", 
            "BASIC_SUMMARY", 
            text="这是一段测试文本",
            max_length=100
        )
        print("基础总结提示词模板加载成功")
        print(f"示例长度: {len(summary_prompt)} 字符")
        
    except Exception as e:
        print(f" 提示词管理器测试失败: {e}")
    
    print()


async def test_ai_model_manager():
    """测试AI模型管理器"""
    print("=== AI模型管理器测试 ===")
    
    try:
        available_services = ai_model_manager.get_available_services()
        print(f"可用服务: {available_services}")
        
        if available_services:
            print("AI模型管理器初始化成功")
        else:
            print("没有可用的AI服务（可能是API密钥未配置）")
            
    except Exception as e:
        print(f"AI模型管理器测试失败: {e}")
    
    print()


async def test_translation_service():
    """测试翻译服务"""
    print("=== 翻译服务测试 ===")
    
    try:
        service = TranslationService()
        models = service.get_available_models()
        print(f"翻译服务可用模型: {models}")
        
        if models:
            print("翻译服务初始化成功")
        else:
            print("翻译服务没有可用模型")
        
        # 注意：这里不进行实际的AI调用测试，因为可能没有配置API密钥
        print("实际AI调用需要配置相应的API密钥")
        
    except Exception as e:
        print(f"✗ 翻译服务测试失败: {e}")
    
    print()


async def test_mock_translation():
    """模拟翻译测试（不调用实际AI）"""
    print("=== 模拟翻译测试 ===")
    
    try:
        service = TranslationService()
        
        # 这些调用会因为没有API密钥而失败，但我们可以看到错误处理
        print("尝试中译英...")
        result = await service.zh2en("你好")
        print(f"结果: {result}")
        
        print("尝试总结...")
        result = await service.summarize("这是一段很长的文本，需要进行总结。" * 10)
        print(f"结果: {result}")
        
    except Exception as e:
        print(f"模拟翻译测试出现异常: {e}")
    
    print()


def print_usage_tips():
    """打印使用提示"""
    print("=== 使用提示 ===")
    print("1. 复制 .env.example 为 .env 并配置API密钥")
    print("2. 根据需要修改 config.yaml 中的模型配置")
    print("3. 启动服务: python main.py")
    print("4. 访问 http://localhost:8000/docs 查看API文档")
    print("5. 测试API: GET http://localhost:8000/api/translate/models")
    print()


async def main():
    """主函数"""
    print("AI大模型翻译服务集成测试\n")
    
    await test_config()
    await test_prompt_manager()
    await test_ai_model_manager()
    await test_translation_service()
    await test_mock_translation()
    
    print_usage_tips()
    
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())