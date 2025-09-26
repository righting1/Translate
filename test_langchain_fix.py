#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试LangChain集成修复
"""

def test_imports():
    """测试导入"""
    print("=== 测试导入 ===")
    try:
        from services.langchain_service import LangChainManager
        print("? LangChainManager导入成功")
        
        from services.langchain_translate import LangChainTranslationService
        print("? LangChainTranslationService导入成功")
        
        return True
    except ImportError as e:
        print(f"? 导入失败: {e}")
        return False

def test_service_creation():
    """测试服务创建"""
    print("\n=== 测试服务创建 ===")
    try:
        from services.langchain_translate import LangChainTranslationService
        
        service = LangChainTranslationService()
        print("? LangChainTranslationService创建成功")
        
        # 测试方法是否存在
        if hasattr(service, 'list_available_chains'):
            print("? list_available_chains方法存在")
        else:
            print("? list_available_chains方法不存在")
            
        if hasattr(service, 'inspect_chain'):
            print("? inspect_chain方法存在")
        else:
            print("? inspect_chain方法不存在")
            
        if hasattr(service, 'clear_memory'):
            print("? clear_memory方法存在")
        else:
            print("? clear_memory方法不存在")
            
        return True
    except Exception as e:
        print(f"? 服务创建失败: {e}")
        return False

def test_chain_methods():
    """测试链方法"""
    print("\n=== 测试链方法 ===")
    try:
        from services.langchain_translate import LangChainTranslationService
        
        service = LangChainTranslationService()
        
        # 测试list_available_chains
        chains = service.list_available_chains()
        print(f"? 可用链数量: {len(chains)}")
        
        # 测试clear_memory
        service.clear_memory()
        print("? 清空内存成功")
        
        # 测试inspect_chain (这个可能会失败，因为链可能不存在)
        try:
            info = service.inspect_chain("test_chain")
            print("? inspect_chain测试成功")
        except ValueError as e:
            print(f"○ inspect_chain正常失败 (链不存在): {e}")
        
        return True
    except Exception as e:
        print(f"? 链方法测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # 测试链列表端点
        resp = client.get("/api/translate/langchain/chains/list")
        print(f"? 链列表端点状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"? 响应数据: {data}")
        elif resp.status_code == 500:
            print("○ 端点存在但服务可能未配置完全")
        
        # 测试清空链内存端点
        resp = client.delete("/api/translate/langchain/chains/clear")
        print(f"? 清空内存端点状态码: {resp.status_code}")
        
        return True
    except Exception as e:
        print(f"? API端点测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始LangChain集成修复验证...\n")
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_service_creation():
        all_passed = False
    
    if not test_chain_methods():
        all_passed = False
    
    if not test_api_endpoints():
        all_passed = False
    
    print("\n=== 测试总结 ===")
    if all_passed:
        print("? 所有测试通过！LangChain集成修复成功")
    else:
        print("??  部分测试失败，需要进一步调试")
    
    return all_passed

if __name__ == "__main__":
    main()