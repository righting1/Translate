"""
测试配置和fixtures
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_model import AIModelManager


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_ai_services():
    """Mock AI服务以避免需要真实的API key"""
    # 创建mock服务
    mock_service = MagicMock()
    mock_service.chat_completion = AsyncMock(return_value="Mocked response")
    mock_service.text_completion = AsyncMock(return_value="Mocked translation")

    # Mock AIModelManager
    original_init = AIModelManager.__init__
    original_get_service = AIModelManager.get_service
    original_get_available_services = AIModelManager.get_available_services

    def mock_init(self):
        self._services = {'mock_openai': mock_service}
        self._default_service = 'mock_openai'

    def mock_get_service(self, service_name=None):
        return mock_service

    def mock_get_available_services(self):
        return ['mock_openai']

    # 替换方法
    AIModelManager.__init__ = mock_init
    AIModelManager.get_service = mock_get_service
    AIModelManager.get_available_services = mock_get_available_services

    yield

    # 恢复原始方法
    AIModelManager.__init__ = original_init
    AIModelManager.get_service = original_get_service
    AIModelManager.get_available_services = original_get_available_services


@pytest.fixture
def test_env():
    """设置测试环境变量"""
    # 保存原始环境变量
    original_env = dict(os.environ)

    # 设置测试用的环境变量
    os.environ.update({
        'OPENAI_API_KEY': 'test_key',
        'DEBUG': 'true',
        'TESTING': 'true'
    })

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)