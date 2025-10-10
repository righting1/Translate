# 配置约定与优先级

## 目标
- 避免“多份 config.yaml”导致的行为不一致
- 明确环境变量、根级配置与子模块配置的优先级与合并策略

## 配置来源
1) 环境变量（.env + 进程环境）
2) 根级配置：config.yaml
3) 模块内置配置：app/config.yaml（如存在）

## 加载与优先级
- 最终配置 = 深度合并(root config.yaml, app/config.yaml)，并由环境变量进行覆盖
- 优先级从高到低：
  1. 环境变量（env）最高
  2. app/config.yaml（模块级别）
  3. 根级 config.yaml（全局默认）

## 建议
- 如果 app/config.yaml 与根级 config.yaml 存在重复字段，保持键路径一致，便于深度合并
- 在 README 中明确“唯一权威入口”为根级 config.yaml，app/config.yaml 仅用于模块覆盖
- 对外展示与文档仅展示根级 config.yaml 示例，避免认知分裂

## 示例（YAML 片段）
root: config.yaml
```yaml
app:
  app_name: "Translate API"
  debug: true
  log_level: "info"

ai_model:
  default_model: "dashscope"
```

module: app/config.yaml
```yaml
app:
  debug: false      # 模块覆盖
  log_level: "warning"
```

环境变量覆盖（.env）
```
LOG_LEVEL=error     # 最终为 error
```

## 实现提示
- 在配置加载器中：
  - 先读根级 config.yaml
  - 再尝试读 app/config.yaml，进行“深度合并”（dict 递归合并）
  - 最后套用环境变量覆盖（支持 ${ENV_VAR} 插值）
- 若项目已存在多个配置加载器（如 core/config_manager.py 与 core/simple_config.py），请合并为一个入口，避免团队误用。