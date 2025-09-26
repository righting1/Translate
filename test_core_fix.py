#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
�򻯵�LangChain�������
"""
import sys
import os

# �����Ŀ��Ŀ¼��·��
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """�������ü���"""
    try:
        from core.config import settings
        print("? ���ü��سɹ�")
        
        if settings.ai_model:
            print(f"? AIģ�����ô��ڣ����� {len(settings.ai_model)} ��������")
            print(f"  - Ĭ��ģ��: {settings.ai_model.get('default_model', 'None')}")
            
            # �г�����ģ�����ã��ų���ģ�����ã�
            excluded_keys = {"default_model"}
            model_configs = {k: v for k, v in settings.ai_model.items() if k not in excluded_keys}
            print(f"  - ���õ�ģ��: {list(model_configs.keys())}")
        else:
            print("? AIģ�����ò�����")
            
        return True
    except Exception as e:
        print(f"? ���ü���ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_manager():
    """����LangChain������"""
    try:
        from services.langchain_service import LangChainManager
        
        print("��ʼ����LangChainManager...")
        manager = LangChainManager()
        print("? LangChainManager�����ɹ�")
        
        print(f"  - �Ѵ����ķ�������: {len(manager.services)}")
        if manager.services:
            print(f"  - �����б�: {list(manager.services.keys())}")
        
        return True
    except Exception as e:
        print(f"? LangChainManager����ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_service():
    """���Է������"""
    try:
        from services.langchain_translate import LangChainTranslationService
        
        print("��ʼ����LangChainTranslationService...")
        service = LangChainTranslationService(use_chains=False)  # ��ʹ�������򻯲���
        print("? LangChainTranslationService�����ɹ�")
        
        # ����Ҫ�ķ���
        methods = ['translate', 'summarize', 'list_available_chains']
        for method in methods:
            if hasattr(service, method):
                print(f"  ? {method} ��������")
            else:
                print(f"  ? {method} ����������")
        
        return True
    except Exception as e:
        print(f"? LangChainTranslationService����ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """�����Ժ���"""
    print("=== LangChain�����޸���֤ ===\n")
    
    print("1. �������ü���...")
    config_ok = test_config_loading()
    
    print("\n2. ����LangChain������...")
    manager_ok = test_langchain_manager()
    
    print("\n3. ���Է������...")
    service_ok = test_translation_service()
    
    print(f"\n=== �����ܽ� ===")
    print(f"���ü���: {'?' if config_ok else '?'}")
    print(f"LangChain������: {'?' if manager_ok else '?'}")
    print(f"�������: {'?' if service_ok else '?'}")
    
    if config_ok and manager_ok and service_ok:
        print("\n? ���Ĺ��ܲ���ͨ����")
        return True
    else:
        print("\n? ����������Ҫ�޸�")
        return False

if __name__ == "__main__":
    main()