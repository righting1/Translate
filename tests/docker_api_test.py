import os
import sys
import time
import argparse
from typing import Optional, Tuple, Dict, Any, List

import pytest
import requests


###############################################################################
# 配置与工具
###############################################################################

DEFAULT_BASE = os.getenv("DOCKER_API_BASE") or os.getenv("API_BASE") or "http://localhost:8000"
DEFAULT_TIMEOUT = float(os.getenv("DOCKER_API_TIMEOUT") or 20)
DEFAULT_MODEL = os.getenv("DOCKER_TEST_MODEL") or None
SKIP_STREAM = os.getenv("DOCKER_SKIP_STREAM", "false").lower() in ("1", "true", "yes")
SKIP_LANGCHAIN = os.getenv("DOCKER_SKIP_LANGCHAIN", "false").lower() in ("1", "true", "yes")
SKIP_ASYNC = os.getenv("DOCKER_SKIP_ASYNC", "false").lower() in ("1", "true", "yes")


class ResultCounter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.warnings: List[str] = []

    def pass_(self):
        self.passed += 1

    def fail(self):
        self.failed += 1

    def skip(self):
        self.skipped += 1


COUNTER = ResultCounter()


###############################################################################
# pytest fixtures
###############################################################################

@pytest.fixture
def base():
    """基础URL fixture"""
    return DEFAULT_BASE


@pytest.fixture 
def timeout():
    """超时时间 fixture"""  
    return DEFAULT_TIMEOUT


@pytest.fixture
def model():
    """模型名称 fixture"""
    return DEFAULT_MODEL


def _print_pass(name: str, extra: str = ""):
    COUNTER.pass_()
    msg = f"[PASS] {name}"
    if extra:
        msg += f" - {extra}"
    print(msg)


def _print_fail(name: str, err: Exception | str):
    COUNTER.fail()
    print(f"[FAIL] {name}: {err}")


def _print_skip(name: str, reason: str):
    COUNTER.skip()
    print(f"[SKIP] {name}: {reason}")


def _print_warn(msg: str):
    COUNTER.warnings.append(msg)
    print(f"[WARN] {msg}")


def http_get(url: str, timeout: float, **kwargs):
    return requests.get(url, timeout=timeout, **kwargs)


def http_post(url: str, json: dict, timeout: float, **kwargs):
    return requests.post(url, json=json, timeout=timeout, **kwargs)


def discover_model(base: str, timeout: float, preferred: Optional[str]) -> Optional[str]:
    try:
        r = http_get(f"{base}/api/translate/models", timeout=timeout)
        if r.status_code != 200:
            _print_warn(f"/api/translate/models 非 200: {r.status_code}")
            return preferred
        data = r.json() or {}
        models = data.get("models") or []
        if preferred:
            return preferred
        if models:
            _print_pass("GET /api/translate/models", f"models={models}")
            return models[0]
        _print_warn("未返回可用模型，将使用默认模型或服务端默认配置")
        return None
    except Exception as e:
        _print_warn(f"获取模型列表失败：{e}")
        return preferred


###############################################################################
# 基础 v1 测试
###############################################################################

def test_health(base: str, timeout: float):
    name = "GET /api/v1/health"
    try:
        resp = http_get(f"{base}/api/v1/health", timeout=timeout)
        assert resp.status_code == 200
        assert (resp.json() or {}).get("status") == "ok"
        _print_pass(name)
    except Exception as e:
        _print_fail(name, e)


def test_greet(base: str, timeout: float):
    name = "GET /api/v1/greet/{name}"
    try:
        resp = http_get(f"{base}/api/v1/greet/Tester", timeout=timeout)
        assert resp.status_code == 200
        msg = (resp.json() or {}).get("message", "")
        assert "Hello" in msg
        _print_pass(name, msg)
    except Exception as e:
        _print_fail(name, e)


###############################################################################
# translate 同步功能
###############################################################################

def test_features(base: str, timeout: float):
    name = "GET /api/translate/features"
    try:
        resp = http_get(f"{base}/api/translate/features", timeout=timeout)
        assert resp.status_code == 200
        feats = (resp.json() or {}).get("features")
        assert isinstance(feats, list) and len(feats) > 0
        _print_pass(name, f"features={len(feats)}")
    except Exception as e:
        _print_fail(name, e)


def test_prompt_types_and_validate(base: str, timeout: float):
    name1 = "GET /api/translate/prompt-types"
    name2 = "POST /api/translate/validate-prompt"
    try:
        r = http_get(f"{base}/api/translate/prompt-types", timeout=timeout)
        assert r.status_code == 200
        data = r.json() or {}
        pts = data.get("prompt_types")
        cats = data.get("categories")
        picked_cat = None
        picked_type = None
        # 兼容 prompt_types 为 list 或 dict
        if isinstance(pts, dict):
            # 结构如 {category: [type1, type2, ...], ...}
            for cat, type_list in pts.items():
                if isinstance(type_list, list) and type_list:
                    picked_cat = cat
                    picked_type = type_list[0]
                    break
            cats = cats or list(pts.keys())
        elif isinstance(pts, list):
            # [{category, types: {...}}, ...] 或 [{name, types: {...}}, ...]
            for item in pts:
                if isinstance(item, dict):
                    cat_val = item.get("category") or item.get("name")
                    types_dict = item.get("types")
                    if cat_val and isinstance(types_dict, dict) and types_dict:
                        picked_cat = cat_val
                        picked_type = next(iter(types_dict.keys()), None)
                        break
            cats = cats or [item.get("category") or item.get("name") for item in pts if isinstance(item, dict)]
        else:
            _print_warn(f"prompt_types 格式未知: {type(pts)}，跳过 validate")
            COUNTER.skip()
            return
        if not cats or not isinstance(cats, list):
            cats = []
        _print_pass(name1, f"categories={len(cats)}")

        if not picked_cat or not picked_type:
            _print_warn("没有找到可验证的提示词类型，跳过 validate")
            COUNTER.skip()
            return

        vr = http_post(
            f"{base}/api/translate/validate-prompt",
            json={"category": picked_cat, "prompt_type": picked_type},
            timeout=timeout,
        )
        assert vr.status_code == 200, vr.text
        res = vr.json() or {}
        if isinstance(res, dict):
            assert res.get("valid", True) is True
        _print_pass(name2, f"{picked_cat}:{picked_type}")
    except Exception as e:
        _print_fail(f"{name1} & {name2}", e)


def test_translate_run(base: str, timeout: float, model: Optional[str]):
    tasks = [
        ("zh2en", "你好，世界！"),
        ("en2zh", "Hello, world!"),
        ("auto_translate", "你好 FastAPI. This is a mixed language sentence."),
        ("summarize", "FastAPI is a modern, fast web framework for building APIs with Python."),
        ("keyword_summary", "Python, FastAPI, async, performance, typing, pydantic"),
        ("structured_summary", "Please summarize this article in a structured way."),
    ]
    for task, text in tasks:
        name = f"POST /api/translate/run ({task})"
        try:
            payload = {"text": text, "task": task}
            if model:
                payload["model"] = model
            r = http_post(f"{base}/api/translate/run", json=payload, timeout=timeout)
            assert r.status_code == 200, r.text
            data = r.json() or {}
            assert data.get("translated_text") or data.get("result")
            _print_pass(name)
        except Exception as e:
            _print_fail(name, e)


def test_translate_endpoints(base: str, timeout: float, model: Optional[str]):
    tests = [
        ("POST /api/translate/zh2en", f"{base}/api/translate/zh2en", {"text": "你好"}),
        ("POST /api/translate/en2zh", f"{base}/api/translate/en2zh", {"text": "Hello"}),
        ("POST /api/translate/auto", f"{base}/api/translate/auto", {"text": "Mixed 语言 content"}),
        ("POST /api/translate/summarize", f"{base}/api/translate/summarize", {"text": "FastAPI is great."}),
        ("POST /api/translate/keyword-summary", f"{base}/api/translate/keyword-summary", {"text": "Python, FastAPI, async"}),
        ("POST /api/translate/structured-summary", f"{base}/api/translate/structured-summary", {"text": "Structure this summary."}),
    ]
    for name, url, payload in tests:
        try:
            if model:
                payload = dict(payload)
                payload["model"] = model
            r = http_post(url, json=payload, timeout=timeout)
            assert r.status_code == 200, r.text
            data = r.json() or {}
            assert data.get("translated_text") or data.get("result")
            _print_pass(name)
        except Exception as e:
            _print_fail(name, e)


###############################################################################
# LangChain 相关
###############################################################################

def test_langchain_endpoints(base: str, timeout: float, model: Optional[str]):
    if SKIP_LANGCHAIN:
        _print_skip("LangChain 全部测试", "环境变量设置跳过")
        return

    # 通用 translate
    try:
        payload = {"text": "你好，世界！", "target_language": "英文"}
        if model:
            payload["model"] = model
        r = http_post(f"{base}/api/translate/langchain/translate", json=payload, timeout=timeout)
        assert r.status_code == 200, r.text
        _print_pass("POST /api/translate/langchain/translate")
    except Exception as e:
        _print_fail("POST /api/translate/langchain/translate", e)

    # zh2en / en2zh / summarize
    lc_tests = [
        ("POST /api/translate/langchain/zh2en", f"{base}/api/translate/langchain/zh2en", {"text": "你好"}),
        ("POST /api/translate/langchain/en2zh", f"{base}/api/translate/langchain/en2zh", {"text": "Hello"}),
        ("POST /api/translate/langchain/summarize", f"{base}/api/translate/langchain/summarize", {"text": "FastAPI is fast."}),
    ]
    for name, url, payload in lc_tests:
        try:
            if model:
                payload = dict(payload)
                payload["model"] = model
            r = http_post(url, json=payload, timeout=timeout)
            assert r.status_code == 200, r.text
            _print_pass(name)
        except Exception as e:
            _print_fail(name, e)

    # chains list / inspect / clear
    try:
        r = http_get(f"{base}/api/translate/langchain/chains/list", timeout=timeout)
        assert r.status_code == 200, r.text
        chains = (r.json() or {}).get("available_chains", [])
        _print_pass("GET /api/translate/langchain/chains/list", f"count={len(chains)}")

        if chains:
            # 只取链名字符串
            cn = chains[0]
            if isinstance(cn, dict):
                chain_name = cn.get("name") or next(iter(cn.values()), None)
            else:
                chain_name = str(cn)
            r2 = http_post(f"{base}/api/translate/langchain/chains/inspect/{chain_name}", json={}, timeout=timeout)
            assert r2.status_code == 200, r2.text
            _print_pass("POST /api/translate/langchain/chains/inspect/{chain_name}", f"{chain_name}")
        else:
            _print_warn("无可用链，跳过 inspect")
            COUNTER.skip()

        r3 = requests.delete(f"{base}/api/translate/langchain/chains/clear", timeout=timeout)
        assert r3.status_code == 200, r3.text
        _print_pass("DELETE /api/translate/langchain/chains/clear")
    except Exception as e:
        _print_fail("LangChain 链管理", e)


###############################################################################
# 异步任务相关
###############################################################################

def _wait_for_task(base: str, task_id: str, timeout: float, poll_interval: float = 1.0) -> Dict[str, Any]:
    end = time.time() + timeout
    last = None
    while time.time() < end:
        r = http_get(f"{base}/api/translate/async/status/{task_id}", timeout=timeout)
        if r.status_code != 200:
            time.sleep(poll_interval)
            continue
        st = r.json() or {}
        last = st
        if (st.get("status") or "").lower() in ("completed", "failed", "expired"):
            return st
        time.sleep(poll_interval)
    return last or {"status": "timeout"}


def test_async_endpoints(base: str, timeout: float, model: Optional[str]):
    if SKIP_ASYNC:
        _print_skip("Async 全部测试", "环境变量设置跳过")
        return

    submit_tests = [
        ("zh2en", f"{base}/api/translate/async/zh2en", {"text": "你好"}),
        ("en2zh", f"{base}/api/translate/async/en2zh", {"text": "Hello"}),
        ("summarize", f"{base}/api/translate/async/summarize", {"text": "FastAPI is fast."}),
        ("keyword-summary", f"{base}/api/translate/async/keyword-summary", {"text": "Python, FastAPI, async"}),
        ("structured-summary", f"{base}/api/translate/async/structured-summary", {"text": "Structure this."}),
    ]

    task_ids: List[str] = []

    for task_name, url, payload in submit_tests:
        name = f"POST {url}"
        try:
            if model:
                payload = dict(payload)
                payload["model"] = model
            r = http_post(url, json=payload, timeout=timeout)
            assert r.status_code == 200, r.text
            tid = (r.json() or {}).get("task_id")
            assert tid
            task_ids.append(tid)
            _print_pass(name, f"task_id={tid}")
        except Exception as e:
            _print_fail(name, e)

    # 轮询第一个任务
    if task_ids:
        tid = task_ids[0]
        st = _wait_for_task(base, tid, timeout=max(timeout, 60))
        if st.get("status") == "completed":
            _print_pass("GET /api/translate/async/status/{task_id}", f"{tid}: completed")
        else:
            _print_warn(f"任务未完成或失败: {tid}, status={st.get('status')}")

        # 获取结果
        try:
            rr = http_get(f"{base}/api/translate/async/result/{tid}", timeout=timeout)
            if rr.status_code == 200:
                _print_pass("GET /api/translate/async/result/{task_id}")
            else:
                _print_warn(f"获取结果非 200: {rr.status_code}")
        except Exception as e:
            _print_warn(f"获取结果异常: {e}")

        # 便捷别名
        try:
            rx = http_get(f"{base}/api/translate/async/{tid}", timeout=timeout)
            if rx.status_code in (200, 404):
                _print_pass("GET /api/translate/async/{task_id}")
            else:
                _print_warn(f"别名接口返回: {rx.status_code}")
        except Exception as e:
            _print_warn(f"别名接口异常: {e}")

    # 任务列表与统计
    try:
        lt = http_get(f"{base}/api/translate/async/tasks", timeout=timeout)
        assert lt.status_code == 200, lt.text
        _print_pass("GET /api/translate/async/tasks")
        st = http_get(f"{base}/api/translate/async/stats", timeout=timeout)
        assert st.status_code == 200, st.text
        _print_pass("GET /api/translate/async/stats")
    except Exception as e:
        _print_fail("异步任务列表或统计", e)

    # 取消测试（提交一个任务后立即取消）
    try:
        r = http_post(f"{base}/api/translate/async/summarize", json={"text": "cancel me"}, timeout=timeout)
        assert r.status_code == 200, r.text
        tid = (r.json() or {}).get("task_id")
        assert tid
        rc = requests.delete(f"{base}/api/translate/async/cancel/{tid}", timeout=timeout)
        if rc.status_code == 200:
            _print_pass("DELETE /api/translate/async/cancel/{task_id}")
        else:
            _print_warn(f"取消返回码: {rc.status_code}")
    except Exception as e:
        _print_warn(f"取消任务异常: {e}")


###############################################################################
# 流式（SSE）
###############################################################################

def _read_sse_chunks(resp: requests.Response, max_lines: int = 5, max_seconds: float = 10.0) -> int:
    start = time.time()
    count = 0
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        # SSE 通常形如 "data: ..."
        if line.startswith("data:"):
            count += 1
        if count >= max_lines or (time.time() - start) > max_seconds:
            break
    return count


def test_stream_endpoints(base: str, timeout: float, model: Optional[str]):
    if SKIP_STREAM:
        _print_skip("SSE 流式 全部测试", "环境变量设置跳过")
        return

    tests = [
        ("POST /api/translate/stream/zh2en", f"{base}/api/translate/stream/zh2en", {"text": "你好"}),
        ("POST /api/translate/stream/en2zh", f"{base}/api/translate/stream/en2zh", {"text": "Hello"}),
        ("POST /api/translate/stream/summarize", f"{base}/api/translate/stream/summarize", {"text": "FastAPI streaming test."}),
    ]
    for name, url, payload in tests:
        try:
            if model:
                payload = dict(payload)
                payload["model"] = model
            with requests.post(url, json=payload, timeout=timeout, stream=True) as resp:
                assert resp.status_code == 200, resp.text
                got = _read_sse_chunks(resp)
                assert got >= 1
                _print_pass(name, f"chunks={got}")
        except Exception as e:
            _print_fail(name, e)


###############################################################################
# 主流程
###############################################################################

def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser(description="Translate API 全量端点测试")
    parser.add_argument("--base", default=DEFAULT_BASE, help="API 基础地址，如 http://localhost:8000")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="每个请求的超时时间（秒）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="优先使用的模型名，未提供则自动从 /models 选择")
    parser.add_argument("--skip-stream", action="store_true", help="跳过流式接口测试")
    parser.add_argument("--skip-langchain", action="store_true", help="跳过 LangChain 接口测试")
    parser.add_argument("--skip-async", action="store_true", help="跳过异步接口测试")
    args = parser.parse_args(argv)

    base = args.base.rstrip("/")
    timeout = float(args.timeout)

    if args.skip_stream:
        global SKIP_STREAM
        SKIP_STREAM = True
    if args.skip_langchain:
        global SKIP_LANGCHAIN
        SKIP_LANGCHAIN = True
    if args.skip_async:
        global SKIP_ASYNC
        SKIP_ASYNC = True

    print("== Translate API 端到端测试 ==")
    print(f"Base URL: {base}")

    # 先做基础检查
    test_health(base, timeout)
    test_greet(base, timeout)

    # 探测模型
    model = discover_model(base, timeout, args.model)
    if model:
        print(f"Using model: {model}")
    else:
        print("Using model: <server default>")

    # 同步与配置相关
    test_features(base, timeout)
    test_prompt_types_and_validate(base, timeout)
    test_translate_run(base, timeout, model)
    test_translate_endpoints(base, timeout, model)

    # LangChain
    test_langchain_endpoints(base, timeout, model)

    # 异步
    test_async_endpoints(base, timeout, model)

    # 流式
    test_stream_endpoints(base, timeout, model)

    print("\n== 测试结果 ==")
    print(f"Passed: {COUNTER.passed}")
    print(f"Failed: {COUNTER.failed}")
    print(f"Skipped: {COUNTER.skipped}")
    if COUNTER.warnings:
        print("Warnings:")
        for w in COUNTER.warnings:
            print(f" - {w}")

    # 若存在失败，用非零码退出，方便 CI/脚本判定
    if COUNTER.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
