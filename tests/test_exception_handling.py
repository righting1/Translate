"""
�����쳣�������
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
    """���Կ��ı�����"""
    # ���Կ��ַ���
    response = client.post("/api/translate/zh2en", json={"text": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["error"].lower()
    
    # ����ֻ�пո���ı�
    response = client.post("/api/translate/zh2en", json={"text": "   "})
    assert response.status_code == 400


def test_task_not_found():
    """��������δ�ҵ�����"""
    response = client.get("/api/translate/async/status/non-existent-task-id")
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_validation_error():
    """����������֤����"""
    # ȱ�ٱ����ֶ�
    response = client.post("/api/translate/zh2en", json={})
    assert response.status_code == 422
    assert "validation" in response.json()["error"].lower()
    
    # �ֶ����ʹ���
    response = client.post("/api/translate/zh2en", json={"text": 123})
    assert response.status_code == 422


def test_model_api_error_handling():
    """����ģ��API������"""
    # ʹ�ò����ڵ�ģ��
    response = client.post(
        "/api/translate/zh2en",
        json={"text": "�����ı�", "model": "non-existent-model"}
    )
    # Ӧ�÷��ش�����Ӧ������״̬��ȡ����ʵ�֣�
    assert response.status_code in [400, 404, 500, 502, 503]


def test_async_task_submission():
    """�����첽�����ύ�Ĵ�����"""
    # �����ύ
    response = client.post(
        "/api/translate/async/zh2en",
        json={"text": "�����ı�"}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    
    # ���ı��ύ
    response = client.post(
        "/api/translate/async/zh2en",
        json={"text": ""}
    )
    assert response.status_code == 400


def test_error_response_structure():
    """���Դ�����Ӧ�ı�׼�ṹ"""
    response = client.get("/api/translate/async/status/invalid-id")
    assert response.status_code == 404
    
    data = response.json()
    # ��֤��Ӧ���������ֶ�
    assert "error" in data
    assert "status_code" in data
    assert "details" in data
    assert "path" in data
    
    # ��֤״̬��һ����
    assert data["status_code"] == 404


def test_exception_details():
    """�����쳣������Ϣ"""
    response = client.get("/api/translate/async/status/test-task-123")
    assert response.status_code == 404
    
    data = response.json()
    # ��֤��������ID����
    assert "details" in data
    if "task_id" in data["details"]:
        assert data["details"]["task_id"] == "test-task-123"


def test_chain_not_found_error():
    """������δ�ҵ�����"""
    response = client.post("/api/translate/langchain/chains/inspect/non-existent-chain")
    # Ӧ�÷���404�������ʵ��Ĵ���
    assert response.status_code in [404, 500]


def test_validate_prompt_with_invalid_data():
    """������ʾ����֤�Ĵ�����"""
    response = client.post(
        "/api/translate/validate-prompt",
        json={"category": "invalid", "prompt_type": "invalid"}
    )
    # Ӧ�÷��ش�����Ӧ
    assert response.status_code in [400, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
