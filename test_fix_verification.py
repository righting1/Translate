#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
����LangChain�����޸�
"""
import sys
import os
import asyncio

# �����Ŀ��Ŀ¼��·��
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_service_creation():
    """���Է��񴴽�"""
    try:
        from services.langchain_translate import LangChainTranslationService
        service = LangChainTranslationService()
        print("? LangChainTranslationService �����ɹ�")
        
        # ��鷽���Ƿ����
        methods_to_check = [
            'translate', 'summarize', 'list_available_chains', 
            'inspect_chain', 'clear_memory'
        ]
        
        for method_name in methods_to_check:
            if hasattr(service, method_name):
                print(f"? {method_name} ��������")
            else:
                print(f"? {method_name} ����������")
        
        return True
        
    except Exception as e:
        print(f"? ���񴴽�ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_import():
    """����API����"""
    try:
        from api.translate.routes import router
        print("? API·�ɵ���ɹ�")
        
        from schemas.translate import TranslateRequest, TranslateResponse, SummarizeRequest, SummarizeResponse
        print("? Schema����ɹ�")
        
        return True
    except Exception as e:
        print(f"? API����ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """������������"""
    try:
        from services.langchain_service import LangChainManager
        manager = LangChainManager()
        print("? LangChainManager����ʹ����ɹ�")
        
        from prompt.templates import prompt_manager
        print("? prompt_manager����ɹ�")
        
        return True
    except Exception as e:
        print(f"? ��������ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_import():
    """����LangChain�⵼��"""
    try:
        import langchain
        print("? langchain����ɹ�")
        
        import langchain_core
        print("? langchain_core����ɹ�")
        
        import langchain_community
        print("? langchain_community����ɹ�")
        
        return True
    except Exception as e:
        print(f"? LangChain�⵼��ʧ��: {e}")
        return False

async def main():
    """�����Ժ���"""
    print("=== LangChain�����޸���֤ ===\n")
    
    print("1. ����LangChain�⵼��...")
    langchain_ok = test_langchain_import()
    
    print("\n2. ������������...")
    deps_ok = test_dependencies()
    
    print("\n3. ���Է��񴴽�...")
    service_ok = await test_service_creation()
    
    print("\n4. ����API����...")
    api_ok = test_api_import()
    
    print(f"\n=== �����ܽ� ===")
    print(f"LangChain��: {'?' if langchain_ok else '?'}")
    print(f"��������: {'?' if deps_ok else '?'}")
    print(f"���񴴽�: {'?' if service_ok else '?'}")
    print(f"API����: {'?' if api_ok else '?'}")
    
    if langchain_ok and deps_ok and service_ok and api_ok:
        print("\n? ���в���ͨ����LangChain�����޸���ɣ�")
        return True
    else:
        print("\n? ����������Ҫ�޸�")
        return False

if __name__ == "__main__":
    asyncio.run(main())