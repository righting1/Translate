import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_streaming_end_to_end(monkeypatch):
    """
    一个方法覆盖三种流式接口（zh2en、en2zh、summarize），验证能持续收到数据块。
    使用 TestClient 的 iter_lines 来读取 SSE 数据。
    """

    # 内联打桩，避免外部模型调用
    class FakeStreamSvc:
        def __init__(self, *args, **kwargs):
            pass

    import services.langchain_translate as lct
    import services.langchain_service as lcs

    # 替换 LangChainTranslationService 以仍然走 langchain_manager 的流接口
    monkeypatch.setattr(lct, "LangChainTranslationService", lct.LangChainTranslationService)

    # 替换底层 BaseLangChainService.generate_text_stream，使其产生稳定的分片
    async def fake_gen_stream(self, prompt: str, **kwargs):
        text = "STREAM-DATA-" + prompt[:8]
        for i in range(0, len(text), 6):
            yield text[i:i+6]

    monkeypatch.setattr(lcs.BaseLangChainService, "generate_text_stream", fake_gen_stream, raising=True)

    def _collect_data_lines(resp, max_chunks=2):
        collected = []
        for raw in resp.iter_lines():
            if not raw:
                continue
            # 兼容 bytes/str 两种情况
            line = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else raw
            if line.startswith("data: "):
                collected.append(line[len("data: "):])
                if len(collected) >= max_chunks:
                    break
        return collected

    # 1) zh2en 流式
    r1 = client.post("/api/translate/stream/zh2en", json={"text": "你好，世界"})
    assert r1.status_code == 200
    chunks = _collect_data_lines(r1)
    assert len(chunks) >= 1

    # 2) en2zh 流式
    r2 = client.post("/api/translate/stream/en2zh", json={"text": "Hello world"})
    assert r2.status_code == 200
    chunks2 = _collect_data_lines(r2)
    assert len(chunks2) >= 1

    # 3) summarize 流式
    r3 = client.post("/api/translate/stream/summarize", json={"text": "AI 帮助提升效率"})
    assert r3.status_code == 200
    chunks3 = _collect_data_lines(r3)
    assert len(chunks3) >= 1
