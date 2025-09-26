#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LangChain 中英文翻译接口
"""
import asyncio
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_langchain_zh2en():
    """测试 LangChain 中文翻译成英文"""
    print("=" * 50)
    print("测试 LangChain zh2en 接口")
    print("=" * 50)
    
    response = client.post(
        "/api/translate/langchain/zh2en",
        json={"text": "你好，世界！这是一个使用LangChain框架的翻译测试。"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_langchain_en2zh():
    """测试 LangChain 英文翻译成中文"""
    print("=" * 50)
    print("测试 LangChain en2zh 接口")
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
    """测试带模型参数的 LangChain 中文翻译成英文"""
    print("=" * 50)
    print("测试带模型参数的 LangChain zh2en 接口")
    print("=" * 50)
    
    response = client.post(
        "/api/translate/langchain/zh2en?model=dashscope&use_chains=false",
        json={"text": "科学技术是第一生产力，人工智能将改变我们的未来。"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_routes_listing():
    """测试路由列表"""
    print("=" * 50)
    print("检查可用的路由")
    print("=" * 50)
    
    from api.translate.routes import router
    langchain_routes = []
    
    for route in router.routes:
        if hasattr(route, 'path') and 'langchain' in route.path:
            langchain_routes.append({
                'path': route.path,
                'methods': list(route.methods) if hasattr(route, 'methods') else []
            })
    
    print(f"LangChain 路由:")
    for route in langchain_routes:
        print(f"  {route['methods']} {route['path']}")

if __name__ == "__main__":
    print("开始测试 LangChain 中英文翻译接口...")
    
    # 首先检查路由
    test_routes_listing()
    
    # 测试具体接口
    test_langchain_zh2en()
    test_langchain_en2zh()
    test_langchain_zh2en_with_model()
    
    print("\n测试完成！")