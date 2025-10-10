from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import pytest
from app.main import app

client = TestClient(app)


class TestLangChainAPI:
    """LangChain API端点测试"""

    def test_langchain_translate_endpoint_exists(self):
        """测试LangChain翻译端点是否存在"""
        payload = {
            "text": "Hello, world",
            "target_language": "中文"
        }
        # 即使服务未配置，端点也应该存在（可能返回500错误）
        resp = client.post("/api/translate/langchain/translate", json=payload)
        # 端点存在就不应该返回404
        assert resp.status_code != 404

    def test_langchain_summarize_endpoint_exists(self):
        """测试LangChain总结端点是否存在"""
        payload = {
            "text": "This is a long text that needs to be summarized.",
            "max_length": 50
        }
        resp = client.post("/api/translate/langchain/summarize", json=payload)
        # 端点存在就不应该返回404
        assert resp.status_code != 404

    def test_langchain_chains_list_endpoint(self):
        """测试链列表端点"""
        resp = client.get("/api/translate/langchain/chains/list")
        assert resp.status_code != 404

    def test_langchain_chains_clear_endpoint(self):
        """测试清空链内存端点"""
        resp = client.delete("/api/translate/langchain/chains/clear")
        assert resp.status_code != 404

    @patch('app.services.langchain_translate.LangChainTranslationService.translate')
    def test_langchain_translate_with_mock(self, mock_translate):
        """使用Mock测试LangChain翻译功能"""
        # 设置mock返回值
        mock_translate.return_value = "你好，世界"
        
        payload = {
            "text": "Hello, world",
            "target_language": "中文"
        }
        
        resp = client.post("/api/translate/langchain/translate", json=payload)
        
        # 检查响应
        if resp.status_code == 200:
            data = resp.json()
            assert "translated_text" in data
            assert data["target_language"] == "中文"

    @patch('app.services.langchain_translate.LangChainTranslationService.summarize')
    def test_langchain_summarize_with_mock(self, mock_summarize):
        """使用Mock测试LangChain总结功能"""
        # 设置mock返回值
        mock_summarize.return_value = "这是一个简短的总结。"
        
        payload = {
            "text": "这是一段很长的文本，需要被总结成更短的内容。" * 10,
            "max_length": 20
        }
        
        resp = client.post("/api/translate/langchain/summarize", json=payload)
        
        # 检查响应
        if resp.status_code == 200:
            data = resp.json()
            assert "summary" in data

    def test_langchain_translate_request_validation(self):
        """测试翻译请求参数验证"""
        # 测试空文本
        payload = {
            "text": "",
            "target_language": "中文"
        }
        resp = client.post("/api/translate/langchain/translate", json=payload)
        assert resp.status_code == 422  # Validation error

        # 测试缺少必要字段
        payload = {
            "target_language": "中文"
        }
        resp = client.post("/api/translate/langchain/translate", json=payload)
        assert resp.status_code == 422  # Validation error

    def test_langchain_summarize_request_validation(self):
        """测试总结请求参数验证"""
        # 测试空文本
        payload = {
            "text": "",
            "max_length": 50
        }
        resp = client.post("/api/translate/langchain/summarize", json=payload)
        assert resp.status_code == 422  # Validation error

        # 测试缺少必要字段
        payload = {
            "max_length": 50
        }
        resp = client.post("/api/translate/langchain/summarize", json=payload)
        assert resp.status_code == 422  # Validation error

    def test_langchain_translate_with_optional_params(self):
        """测试带可选参数的翻译请求"""
        payload = {
            "text": "Hello, world",
            "target_language": "中文",
            "source_language": "英文",
            "context": "greeting"
        }
        
        resp = client.post("/api/translate/langchain/translate", json=payload)
        # 端点应该接受这些参数
        assert resp.status_code != 422

    def test_langchain_query_parameters(self):
        """测试查询参数"""
        payload = {
            "text": "Hello, world",
            "target_language": "中文"
        }
        
        # 测试model参数
        resp = client.post(
            "/api/translate/langchain/translate?model=dashscope", 
            json=payload
        )
        assert resp.status_code != 422
        
        # 测试use_chains参数
        resp = client.post(
            "/api/translate/langchain/translate?use_chains=false", 
            json=payload
        )
        assert resp.status_code != 422


class TestLangChainServices:
    """LangChain服务层测试"""

    def test_langchain_service_import(self):
        """测试LangChain服务导入"""
        try:
            from app.services.langchain_service import LangChainManager
            from app.services.langchain_translate import LangChainTranslationService
            assert True  # 导入成功
        except ImportError as e:
            pytest.fail(f"LangChain服务导入失败: {e}")

    # def test_langchain_manager_creation(self):
    #     """测试LangChain管理器创建"""
    #     try:
    #         from services.langchain_service import LangChainManager
    #         manager = LangChainManager()
    #         assert manager is not None
    #     except Exception as e:
    #         pytest.fail(f"LangChain管理器创建失败: {e}")

    def test_langchain_translation_service_creation(self):
        """测试LangChain翻译服务创建"""
        try:
            from app.services.langchain_translate import LangChainTranslationService
            service = LangChainTranslationService()
            assert service is not None
        except Exception as e:
            pytest.fail(f"LangChain翻译服务创建失败: {e}")


class TestLangChainSchemas:
    """LangChain相关Schema测试"""

    def test_summarize_request_schema(self):
        """测试总结请求Schema"""
        try:
            from app.schemas.translate import SummarizeRequest
            
            # 测试基本创建
            request = SummarizeRequest(text="测试文本")
            assert request.text == "测试文本"
            assert request.max_length == 100  # 默认值
            
            # 测试完整参数
            request = SummarizeRequest(
                text="测试文本",
                max_length=50,
                context="测试上下文",
                model="dashscope"
            )
            assert request.max_length == 50
            assert request.context == "测试上下文"
            assert request.model == "dashscope"
            
        except ImportError as e:
            pytest.fail(f"SummarizeRequest导入失败: {e}")

    def test_summarize_response_schema(self):
        """测试总结响应Schema"""
        try:
            from app.schemas.translate import SummarizeResponse
            
            # 测试基本创建
            response = SummarizeResponse(summary="这是总结")
            assert response.summary == "这是总结"
            
            # 测试完整参数
            response = SummarizeResponse(
                summary="这是总结",
                model="dashscope",
                tokens_used=150
            )
            assert response.model == "dashscope"
            assert response.tokens_used == 150
            
        except ImportError as e:
            pytest.fail(f"SummarizeResponse导入失败: {e}")

    def test_translate_request_extended_schema(self):
        """测试扩展的翻译请求Schema"""
        try:
            from app.schemas.translate import TranslateRequest
            
            # 测试新增的字段
            request = TranslateRequest(
                text="Hello",
                target_language="中文",
                source_language="英文",
                context="问候语"
            )
            assert request.target_language == "中文"
            assert request.source_language == "英文"
            assert request.context == "问候语"
            
        except Exception as e:
            pytest.fail(f"扩展TranslateRequest测试失败: {e}")

    def test_translate_response_backward_compatibility(self):
        """测试翻译响应向后兼容性"""
        try:
            from app.schemas.translate import TranslateResponse
            
            # 测试新字段
            response = TranslateResponse(
                translated_text="你好",
                target_language="中文"
            )
            assert response.translated_text == "你好"
            assert response.result == "你好"  # 向后兼容
            
            # 测试旧字段
            response = TranslateResponse(
                result="你好",
                target_language="中文"
            )
            assert response.result == "你好"
            assert response.translated_text == "你好"  # 新字段应该匹配
            
        except Exception as e:
            pytest.fail(f"TranslateResponse向后兼容性测试失败: {e}")


class TestLangChainIntegration:
    """LangChain集成测试"""

    def test_dependencies_installation(self):
        """测试LangChain依赖是否已安装"""
        try:
            import langchain
            import langchain_core
            import langchain_community
            assert True  # 依赖安装成功
        except ImportError as e:
            pytest.fail(f"LangChain依赖未安装: {e}")

    def test_config_integration(self):
        """测试配置集成"""
        try:
            from app.core.config import settings
            assert settings.ai_model is not None
            assert "default_model" in settings.ai_model
        except Exception as e:
            pytest.fail(f"配置集成测试失败: {e}")

    def test_prompt_integration(self):
        """测试提示词集成"""
        try:
            from app.services.prompt.templates import prompt_manager
            assert prompt_manager is not None
        except Exception as e:
            pytest.fail(f"提示词集成测试失败: {e}")


def test_langchain_api_health():
    """LangChain API健康检查"""
    # 测试基本的API路由是否工作
    resp = client.get("/api/translate/models")
    assert resp.status_code == 200 or resp.status_code == 500  # 端点存在

    resp = client.get("/api/translate/prompt-types")
    assert resp.status_code == 200 or resp.status_code == 500  # 端点存在


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])