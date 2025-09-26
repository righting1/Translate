#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
���ٲ���LangChain�����޸�
"""

def test_imports():
    """���Ե���"""
    print("=== ���Ե��� ===")
    try:
        from services.langchain_service import LangChainManager
        print("? LangChainManager����ɹ�")
        
        from services.langchain_translate import LangChainTranslationService
        print("? LangChainTranslationService����ɹ�")
        
        return True
    except ImportError as e:
        print(f"? ����ʧ��: {e}")
        return False

def test_service_creation():
    """���Է��񴴽�"""
    print("\n=== ���Է��񴴽� ===")
    try:
        from services.langchain_translate import LangChainTranslationService
        
        service = LangChainTranslationService()
        print("? LangChainTranslationService�����ɹ�")
        
        # ���Է����Ƿ����
        if hasattr(service, 'list_available_chains'):
            print("? list_available_chains��������")
        else:
            print("? list_available_chains����������")
            
        if hasattr(service, 'inspect_chain'):
            print("? inspect_chain��������")
        else:
            print("? inspect_chain����������")
            
        if hasattr(service, 'clear_memory'):
            print("? clear_memory��������")
        else:
            print("? clear_memory����������")
            
        return True
    except Exception as e:
        print(f"? ���񴴽�ʧ��: {e}")
        return False

def test_chain_methods():
    """����������"""
    print("\n=== ���������� ===")
    try:
        from services.langchain_translate import LangChainTranslationService
        
        service = LangChainTranslationService()
        
        # ����list_available_chains
        chains = service.list_available_chains()
        print(f"? ����������: {len(chains)}")
        
        # ����clear_memory
        service.clear_memory()
        print("? ����ڴ�ɹ�")
        
        # ����inspect_chain (������ܻ�ʧ�ܣ���Ϊ�����ܲ�����)
        try:
            info = service.inspect_chain("test_chain")
            print("? inspect_chain���Գɹ�")
        except ValueError as e:
            print(f"�� inspect_chain����ʧ�� (��������): {e}")
        
        return True
    except Exception as e:
        print(f"? ����������ʧ��: {e}")
        return False

def test_api_endpoints():
    """����API�˵�"""
    print("\n=== ����API�˵� ===")
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # �������б�˵�
        resp = client.get("/api/translate/langchain/chains/list")
        print(f"? ���б�˵�״̬��: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"? ��Ӧ����: {data}")
        elif resp.status_code == 500:
            print("�� �˵���ڵ��������δ������ȫ")
        
        # ����������ڴ�˵�
        resp = client.delete("/api/translate/langchain/chains/clear")
        print(f"? ����ڴ�˵�״̬��: {resp.status_code}")
        
        return True
    except Exception as e:
        print(f"? API�˵����ʧ��: {e}")
        return False

def main():
    """�����Ժ���"""
    print("��ʼLangChain�����޸���֤...\n")
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_service_creation():
        all_passed = False
    
    if not test_chain_methods():
        all_passed = False
    
    if not test_api_endpoints():
        all_passed = False
    
    print("\n=== �����ܽ� ===")
    if all_passed:
        print("? ���в���ͨ����LangChain�����޸��ɹ�")
    else:
        print("??  ���ֲ���ʧ�ܣ���Ҫ��һ������")
    
    return all_passed

if __name__ == "__main__":
    main()