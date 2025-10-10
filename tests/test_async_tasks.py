import time
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_async_end_to_end(monkeypatch):
    """
    一个用例覆盖：
    - 提交异步中译英/英译中/总结任务
    - 轮询直到完成
    - 获取结果并断言
    """

    # 内联打桩 LangChainTranslationService，避免外部依赖
    class FakeLangChainService:
        def __init__(self, model_name=None, use_chains=True):
            self.model_name = model_name
            self.use_chains = use_chains

        async def zh2en(self, text: str, **kwargs) -> str:
            return "Hello World (async)"

        async def en2zh(self, text: str, **kwargs) -> str:
            return "你好，世界（异步）"

        async def summarize(self, text: str, max_length: int = 200, **kwargs) -> str:
            return f"摘要({min(max_length, 20)}): {text[:min(len(text), 20)]}"

    import app.services.langchain_translate as lct
    monkeypatch.setattr(lct, "LangChainTranslationService", FakeLangChainService)

    def wait_until_completed(task_id: str, timeout_s: float = 3.0):
        start = time.time()
        while time.time() - start < timeout_s:
            r = client.get(f"/api/translate/async/status/{task_id}")
            assert r.status_code == 200
            data = r.json()
            if data.get("status") == "completed":
                return True
            if data.get("status") == "failed":
                return False
            time.sleep(0.05)
        return False

    # 1) 中译英
    resp_zh2en = client.post("/api/translate/async/zh2en", json={"text": "你好，世界"})
    assert resp_zh2en.status_code == 200
    task_zh2en = resp_zh2en.json().get("task_id")
    assert task_zh2en and wait_until_completed(task_zh2en)
    res_zh2en = client.get(f"/api/translate/async/result/{task_zh2en}")
    assert res_zh2en.status_code == 200
    assert "Hello World" in res_zh2en.json().get("result", "")

    # 2) 英译中
    resp_en2zh = client.post("/api/translate/async/en2zh", json={"text": "Hello, world"})
    assert resp_en2zh.status_code == 200
    task_en2zh = resp_en2zh.json().get("task_id")
    assert task_en2zh and wait_until_completed(task_en2zh)
    res_en2zh = client.get(f"/api/translate/async/result/{task_en2zh}")
    assert res_en2zh.status_code == 200
    assert "你好，世界" in res_en2zh.json().get("result", "")

    # 3) 总结
    resp_sum = client.post("/api/translate/async/summarize", json={"text": "人工智能帮助我们更高效地解决复杂问题。"})
    assert resp_sum.status_code == 200
    task_sum = resp_sum.json().get("task_id")
    assert task_sum and wait_until_completed(task_sum)
    res_sum = client.get(f"/api/translate/async/result/{task_sum}")
    assert res_sum.status_code == 200
    assert "摘要" in res_sum.json().get("result", "")
