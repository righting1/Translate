# Translate API


本项目为一个基于 FastAPI 的示例后端，包含基础的路由、配置与文档体系，便于快速起步与扩展。

## 功能概览
- 健康检查：`GET /api/v1/health`
- 问候接口：`GET /api/v1/greet/{name}`
 - 功能列表：`GET /api/translate/features`
 - 翻译（统一任务）：`POST /api/translate/run`（任务：`zh2en`、`en2zh`、`summarize`）
   - task 字段类型：枚举 `FeatureCode`（`zh2en` | `en2zh` | `summarize`）
 - 翻译（专用端点）：
   - `POST /api/translate/zh2en`
   - `POST /api/translate/en2zh`
   - `POST /api/translate/summarize`

## 快速开始
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

启动后打开浏览器访问：
- 根路径：`http://127.0.0.1:8000/`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

## 文档站点（MkDocs）
```bash
mkdocs serve
```
本地预览地址通常为：`http://127.0.0.1:8000` 或终端提示的端口。

## 项目结构
```
.
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── routes.py            # v1 路由（/api/v1/health, /api/v1/greet/{name}）
├── constants/
│   └── __init__.py
├── core/
│   ├── __init__.py
│   └── config/
│       └── __init__.py          # 应用配置（Pydantic BaseSettings）
├── docs/
│   └── index.md                 # 文档首页（可用 mkdocs 预览）
├── models/
│   └── __init__.py
├── schemas/
│   └── __init__.py
├── services/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── main.py                      # 应用入口，挂载 v1 路由
├── config.yaml                  # YAML 配置文件
├── mkdocs.yml                   # MkDocs 配置
├── requirements.txt             # 依赖
└── test_main.http
```

## 配置
使用 YAML 格式配置文件 `config.yaml`，参见 `core/config/__init__.py` 中 `Settings` 定义：

### 应用配置
- `app_name`: 应用名称（默认：Translate API）
- `debug`: 调试开关（默认：True）
- `host`: 监听主机（默认：127.0.0.1）
- `port`: 监听端口（默认：8000）
- `reload`: 热重载（默认：True）
- `log_level`: 日志级别（默认：info）
- `version`: 应用版本（默认：0.1.0）

### 配置文件示例
项目根目录的 `config.yaml`：
```yaml
app:
  app_name: "Translate API"
  debug: true
  host: "127.0.0.1"
  port: 8000
  reload: true
  log_level: "info"
  version: "0.1.0"

```

### 运行方式
```bash
# 方式一：使用 uvicorn 命令
uvicorn main:app --reload

# 方式二：直接运行（读取 config.yaml 配置）
python main.py
```
