#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
���� LangChain ��Ӣ�ķ���ӿ�
"""
import asyncio
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_langchain_zh2en():
    """���� LangChain ���ķ����Ӣ��"""
    print("=" * 50)
    print("���� LangChain zh2en �ӿ�")
    print("=" * 50)
    
    response = client.post(
        "/api/translate/langchain/zh2en",
        json={"text": "��ã����磡����һ��ʹ��LangChain��ܵķ�����ԡ�"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_langchain_en2zh():
    """���� LangChain Ӣ�ķ��������"""
    print("=" * 50)
    print("���� LangChain en2zh �ӿ�")
    print("=" * 50)
    
    response = client.post(
        "/api/translate/langchain/en2zh",
        json={"text": "Hello, world! This is a translation test using LangChain framework."}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_langchain_zh2en_with_model():
    """���Դ�ģ�Ͳ����� LangChain ���ķ����Ӣ��"""
    print("=" * 50)
    print("���Դ�ģ�Ͳ����� LangChain zh2en �ӿ�")
    print("=" * 50)
    
    response = client.post(
        "/api/translate/langchain/zh2en?model=dashscope&use_chains=false",
        json={"text": "��ѧ�����ǵ�һ���������˹����ܽ��ı����ǵ�δ����"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_routes_listing():
    """����·���б�"""
    print("=" * 50)
    print("�����õ�·��")
    print("=" * 50)
    
    from api.translate.routes import router
    langchain_routes = []
    
    for route in router.routes:
        if hasattr(route, 'path') and 'langchain' in route.path:
            langchain_routes.append({
                'path': route.path,
                'methods': list(route.methods) if hasattr(route, 'methods') else []
            })
    
    print(f"LangChain ·��:")
    for route in langchain_routes:
        print(f"  {route['methods']} {route['path']}")

if __name__ == "__main__":
    print("��ʼ���� LangChain ��Ӣ�ķ���ӿ�...")
    
    # ���ȼ��·��
    test_routes_listing()
    
    # ���Ծ���ӿ�
    test_langchain_zh2en()
    test_langchain_en2zh()
    test_langchain_zh2en_with_model()
    
    print("\n������ɣ�")