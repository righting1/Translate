# 依赖与可复现构建约定

## 目标
- 将生产依赖与开发/文档/测试依赖分离，降低冲突与攻击面。
- 通过锁定文件实现可复现安装，避免「今天能跑，明天挂」的问题。

## 文件划分
- requirements.txt: 仅生产运行所需依赖（FastAPI、Pydantic、LangChain 等）。
- requirements-dev.txt: 仅开发/测试/文档（pytest、coverage、mkdocs、pytest-asyncio、httpx）。
- .gitignore: 排除 __pycache__/、*.pyc、.pytest_cache/、.env 等。

## 版本策略
- 推荐使用 pip-tools 生成锁定文件，确保可复现：
  ```bash
  pip install -U pip-tools
  # 生产锁定
  pip-compile --generate-hashes --output-file requirements.lock requirements.txt
  # 开发锁定（包含生产 + 开发）
  pip-compile --generate-hashes --output-file requirements-dev.lock requirements.txt requirements-dev.txt

  # 安装
  pip-sync requirements.lock           # 生产环境
  pip-sync requirements-dev.lock       # 开发环境
  ```
- LangChain 生态依赖（langchain、langchain-core、langchain-community、langchain-openai、text-splitters）需要严格对齐同一代版本，避免 API 破裂。
- 若运行代码未直接使用 requests/urllib3 或 SQLAlchemy 等，请移除无用依赖以减少供应链风险。

## CI/CD 建议
- CI 使用 `pip-sync requirements-dev.lock` 安装依赖，测试稳定。
- 生产镜像使用 `pip-sync requirements.lock`，体积更小、更安全。

## 常见问题
- httpx vs requests: 项目若仅在测试中使用 httpx，可将其只保留在 requirements-dev.txt。
- orjson/zstandard: 若未被实际导入，可移除。