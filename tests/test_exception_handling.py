"""
测试异常处理机制
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from utils.exceptions import (
    EmptyTextError,
    TaskNotFoundException,
    ModelNotAvailableError,
    AuthenticationError,
    TextTooLongError
)

client = TestClient(app)


def test_empty_text_error():
    """测试空文本错误"""
    # 测试空字符串
    response = client.post("/api/translate/zh2en", json={"text": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["error"].lower()
    
    # 测试只有空格的文本
    response = client.post("/api/translate/zh2en", json={"text": "   "})
    assert response.status_code == 400


def test_task_not_found():
    """测试任务未找到错误"""
    response = client.get("/api/translate/async/status/non-existent-task-id")
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_validation_error():
    """测试请求验证错误"""
    # 缺少必需字段
    response = client.post("/api/translate/zh2en", json={})
    assert response.status_code == 422
    assert "validation" in response.json()["error"].lower()
    
    # 字段类型错误
    response = client.post("/api/translate/zh2en", json={"text": 123})
    assert response.status_code == 422


def test_model_api_error_handling():
    """测试模型API错误处理"""
    # 使用不存在的模型
    response = client.post(
        "/api/translate/zh2en",
        json={"text": "测试文本", "model": "non-existent-model"}
    )
    # 应该返回错误响应（具体状态码取决于实现）
    assert response.status_code in [400, 404, 500, 502, 503]


def test_async_task_submission():
    """测试异步任务提交的错误处理"""
    # 正常提交
    response = client.post(
        "/api/translate/async/zh2en",
        json={"text": "测试文本"}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    
    # 空文本提交
    response = client.post(
        "/api/translate/async/zh2en",
        json={"text": ""}
    )
    assert response.status_code == 400


def test_error_response_structure():
    """测试错误响应的标准结构"""
    response = client.get("/api/translate/async/status/invalid-id")
    assert response.status_code == 404
    
    data = response.json()
    # 验证响应包含必需字段
    assert "error" in data
    assert "status_code" in data
    assert "details" in data
    assert "path" in data
    
    # 验证状态码一致性
    assert data["status_code"] == 404


def test_exception_details():
    """测试异常详情信息"""
    response = client.get("/api/translate/async/status/test-task-123")
    assert response.status_code == 404
    
    data = response.json()
    # 验证包含任务ID详情
    assert "details" in data
    if "task_id" in data["details"]:
        assert data["details"]["task_id"] == "test-task-123"


def test_chain_not_found_error():
    """测试链未找到错误"""
    response = client.post("/api/translate/langchain/chains/inspect/non-existent-chain")
    # 应该返回404或其他适当的错误
    assert response.status_code in [404, 500]


def test_validate_prompt_with_invalid_data():
    """测试提示词验证的错误处理"""
    response = client.post(
        "/api/translate/validate-prompt",
        json={"category": "invalid", "prompt_type": "invalid"}
    )
    # 应该返回错误响应
    assert response.status_code in [400, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
