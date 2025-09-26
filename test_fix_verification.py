#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LangChain服务修复
"""
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_service_creation():
    """测试服务创建"""
    try:
        from services.langchain_translate import LangChainTranslationService
        service = LangChainTranslationService()
        print("? LangChainTranslationService 创建成功")
        
        # 检查方法是否存在
        methods_to_check = [
            'translate', 'summarize', 'list_available_chains', 
            'inspect_chain', 'clear_memory'
        ]
        
        for method_name in methods_to_check:
            if hasattr(service, method_name):
                print(f"? {method_name} 方法存在")
            else:
                print(f"? {method_name} 方法不存在")
        
        return True
        
    except Exception as e:
        print(f"? 服务创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_import():
    """测试API导入"""
    try:
        from api.translate.routes import router
        print("? API路由导入成功")
        
        from schemas.translate import TranslateRequest, TranslateResponse, SummarizeRequest, SummarizeResponse
        print("? Schema导入成功")
        
        return True
    except Exception as e:
        print(f"? API导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试依赖导入"""
    try:
        from services.langchain_service import LangChainManager
        manager = LangChainManager()
        print("? LangChainManager导入和创建成功")
        
        from prompt.templates import prompt_manager
        print("? prompt_manager导入成功")
        
        return True
    except Exception as e:
        print(f"? 依赖导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_import():
    """测试LangChain库导入"""
    try:
        import langchain
        print("? langchain导入成功")
        
        import langchain_core
        print("? langchain_core导入成功")
        
        import langchain_community
        print("? langchain_community导入成功")
        
        return True
    except Exception as e:
        print(f"? LangChain库导入失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=== LangChain服务修复验证 ===\n")
    
    print("1. 测试LangChain库导入...")
    langchain_ok = test_langchain_import()
    
    print("\n2. 测试依赖导入...")
    deps_ok = test_dependencies()
    
    print("\n3. 测试服务创建...")
    service_ok = await test_service_creation()
    
    print("\n4. 测试API导入...")
    api_ok = test_api_import()
    
    print(f"\n=== 测试总结 ===")
    print(f"LangChain库: {'?' if langchain_ok else '?'}")
    print(f"依赖导入: {'?' if deps_ok else '?'}")
    print(f"服务创建: {'?' if service_ok else '?'}")
    print(f"API导入: {'?' if api_ok else '?'}")
    
    if langchain_ok and deps_ok and service_ok and api_ok:
        print("\n? 所有测试通过！LangChain集成修复完成！")
        return True
    else:
        print("\n? 还有问题需要修复")
        return False

if __name__ == "__main__":
    asyncio.run(main())