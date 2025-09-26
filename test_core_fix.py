#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的LangChain服务测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置加载"""
    try:
        from core.config import settings
        print("? 配置加载成功")
        
        if settings.ai_model:
            print(f"? AI模型配置存在，包含 {len(settings.ai_model)} 个配置项")
            print(f"  - 默认模型: {settings.ai_model.get('default_model', 'None')}")
            
            # 列出所有模型配置（排除非模型配置）
            excluded_keys = {"default_model"}
            model_configs = {k: v for k, v in settings.ai_model.items() if k not in excluded_keys}
            print(f"  - 配置的模型: {list(model_configs.keys())}")
        else:
            print("? AI模型配置不存在")
            
        return True
    except Exception as e:
        print(f"? 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_manager():
    """测试LangChain管理器"""
    try:
        from services.langchain_service import LangChainManager
        
        print("开始创建LangChainManager...")
        manager = LangChainManager()
        print("? LangChainManager创建成功")
        
        print(f"  - 已创建的服务数量: {len(manager.services)}")
        if manager.services:
            print(f"  - 服务列表: {list(manager.services.keys())}")
        
        return True
    except Exception as e:
        print(f"? LangChainManager创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_service():
    """测试翻译服务"""
    try:
        from services.langchain_translate import LangChainTranslationService
        
        print("开始创建LangChainTranslationService...")
        service = LangChainTranslationService(use_chains=False)  # 不使用链，简化测试
        print("? LangChainTranslationService创建成功")
        
        # 检查必要的方法
        methods = ['translate', 'summarize', 'list_available_chains']
        for method in methods:
            if hasattr(service, method):
                print(f"  ? {method} 方法存在")
            else:
                print(f"  ? {method} 方法不存在")
        
        return True
    except Exception as e:
        print(f"? LangChainTranslationService创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== LangChain服务修复验证 ===\n")
    
    print("1. 测试配置加载...")
    config_ok = test_config_loading()
    
    print("\n2. 测试LangChain管理器...")
    manager_ok = test_langchain_manager()
    
    print("\n3. 测试翻译服务...")
    service_ok = test_translation_service()
    
    print(f"\n=== 测试总结 ===")
    print(f"配置加载: {'?' if config_ok else '?'}")
    print(f"LangChain管理器: {'?' if manager_ok else '?'}")
    print(f"翻译服务: {'?' if service_ok else '?'}")
    
    if config_ok and manager_ok and service_ok:
        print("\n? 核心功能测试通过！")
        return True
    else:
        print("\n? 还有问题需要修复")
        return False

if __name__ == "__main__":
    main()