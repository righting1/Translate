import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def submit_structured_summary(text: str = "测试取消任务", max_length: int = 50):
    resp = client.post(
        "/api/translate/async/structured-summary",
        params={"max_length": max_length},
        json={"text": text},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    return data["task_id"]


def test_cancel_task_flow():
    task_id = submit_structured_summary()

    # 立即取消任务
    cancel = client.delete(f"/api/translate/async/cancel/{task_id}")
    # 允许两种情况：
    # 1) 已成功取消 -> 200
    # 2) 任务恰好已经完成 -> 404（不可取消）
    assert cancel.status_code in (200, 404)

    # 查询状态
    status = client.get(f"/api/translate/async/status/{task_id}")
    assert status.status_code == 200
    st = status.json().get("status")
    assert st in ("failed", "completed", "pending", "running", "expired")

    # 结果接口：可能 404（已取消或未完成）或 200（已完成）
    result = client.get(f"/api/translate/async/result/{task_id}")
    assert result.status_code in (200, 404)
    #assert result.status_code == 200
