import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.langchain_service import LangChainManager
from services.langchain_translate import LangChainTranslationService


async def test_langchain_services():
    """测试LangChain服务"""
    print("=== LangChain服务测试 ===")

    try:
        # 测试LangChain管理器
        print("\n1. 测试LangChain管理器...")
        manager = LangChainManager()

        # 测试获取服务
        print("可用的服务类型:", manager.get_available_services())

        # 测试DashScope服务
        print("\n2. 测试DashScope服务...")
        dashscope_service = manager.get_service("dashscope")
        if dashscope_service:
            result = await dashscope_service.generate_text("你好，请介绍一下自己")
            print("DashScope响应:", result[:100] + "..." if len(result) > 100 else result)
        else:
            print("DashScope服务未配置")

        # 测试翻译服务
        print("\n3. 测试LangChain翻译服务...")
        translation_service = LangChainTranslationService()

        # 测试翻译
        test_text = "Hello, how are you today?"
        translation_result = await translation_service.translate(
            text=test_text,
            target_language="中文"
        )
        print(f"翻译结果: '{test_text}' -> '{translation_result}'")

        # 测试总结
        print("\n4. 测试文本总结...")
        long_text = """
        人工智能(AI)是计算机科学的一个分支，它试图理解智能的实质，
        并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
        该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
        人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
        """
        summary_result = await translation_service.summarize(
            text=long_text.strip(),
            max_length=50
        )
        print(f"总结结果: {summary_result}")

        # 测试链管理
        print("\n5. 测试链管理...")
        chains = translation_service.list_available_chains()
        print("可用的链:", chains)

        print("\n=== 所有测试完成 ===")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


async def test_api_compatibility():
    """测试API兼容性"""
    print("\n=== API兼容性测试 ===")

    try:
        from api.translate.routes import router
        print("✓ API路由导入成功")

        from schemas.translate import (
            TranslateRequest,
            TranslateResponse,
            SummarizeRequest,
            SummarizeResponse
        )
        print("✓ Schema导入成功")

        # 测试Schema创建
        translate_req = TranslateRequest(
            text="Hello world",
            target_language="中文"
        )
        print(f"✓ TranslateRequest创建成功: {translate_req.text}")

        translate_resp = TranslateResponse(
            translated_text="你好世界",
            target_language="中文"
        )
        print(f"✓ TranslateResponse创建成功: {translate_resp.translated_text}")

        summarize_req = SummarizeRequest(
            text="这是一个很长的文本，需要总结一下内容"
        )
        print(f"✓ SummarizeRequest创建成功: {summarize_req.text}")

        summarize_resp = SummarizeResponse(
            summary="文本总结"
        )
        print(f"✓ SummarizeResponse创建成功: {summarize_resp.summary}")

    except Exception as e:
        print(f"API兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("开始LangChain集成测试...\n")

    await test_api_compatibility()
    await test_langchain_services()

    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main())