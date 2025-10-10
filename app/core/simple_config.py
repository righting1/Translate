# -*- coding: utf-8 -*-
"""
简化的配置管理器
专门为当前项目优化的配置加载器
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import re

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleConfigManager:
    """简化的配置管理器，专门为翻译项目优化"""

    def __init__(
        self,
        config_files: Optional[List[str]] = None,
        dotenv_files: Optional[List[str]] = None,
        env_prefix: Optional[str] = None
    ):
        """
        初始化配置管理器

        Args:
            config_files: 配置文件列表，默认 ["config.yaml", "config.yml"]
            dotenv_files: .env 文件列表，默认 [".env"]
            env_prefix: 环境变量前缀，默认 None (读取所有环境变量)
        """
        self.config_files = config_files or ["config.yaml", "config.yml"]
        self.dotenv_files = dotenv_files or [".env"]
        self.env_prefix = env_prefix
        self._config: Dict[str, Any] = {}

    def _resolve_config_files(self) -> List[Path]:
        """根据环境与常见位置解析配置文件候选路径列表（去重，保持顺序）。"""
        seen = set()
        results: List[Path] = []

        # 1) 显式环境变量优先
        env_path = os.getenv("CONFIG_PATH")
        if env_path:
            p = Path(env_path).expanduser()
            if str(p) not in seen:
                results.append(p)
                seen.add(str(p))

        here = Path(__file__).resolve()
        project_root = here.parents[2]  # .../app/core/simple_config.py -> app -> project_root
        cwd = Path.cwd()

        # 2) 传入的 config_files（相对 CWD）
        for name in (self.config_files or []):
            p = cwd / name
            if str(p) not in seen:
                results.append(p)
                seen.add(str(p))

        # 3) 常见候选位置
        candidates = [
            cwd / "config.yaml",
            cwd / "config.yml",
            cwd / "app" / "config.yaml",
            cwd / "app" / "config.yml",
            project_root / "config.yaml",
            project_root / "config.yml",
            project_root / "app" / "config.yaml",
            project_root / "app" / "config.yml",
            Path("/app/config.yaml"),           # Docker 常见位置
            Path("/app/app/config.yaml"),       # 我们 compose 中显式使用的路径
        ]
        for p in candidates:
            if str(p) not in seen:
                results.append(p)
                seen.add(str(p))

        # 仅返回存在的文件，但先打印尝试列表便于排查
        logger.info("SimpleConfigManager 将尝试的配置路径：%s", [str(p) for p in results])
        existing = [p for p in results if p.exists()]
        if not existing:
            logger.warning("未发现存在的配置文件，请检查 CONFIG_PATH 或文件位置")
        else:
            logger.info("检测到存在的配置文件：%s", [str(p) for p in existing])
        return existing

    def _load_dotenv(self) -> None:
        """加载 .env 文件"""
        if not DOTENV_AVAILABLE:
            logger.warning("python-dotenv 未安装，跳过 .env 文件加载")
            return

        for dotenv_file in self.dotenv_files:
            dotenv_path = Path(dotenv_file)
            if dotenv_path.exists():
                load_dotenv(dotenv_path)
                logger.info(f"已加载 .env 文件: {dotenv_file}")

    def _load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML 未安装，无法加载 YAML 配置文件")

        config_path = Path(file_path)
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {file_path}")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = f.read()
                # 环境变量插值 ${VAR}
                def _repl(m: re.Match) -> str:
                    var = m.group(1)
                    return os.getenv(var, m.group(0))
                raw = re.sub(r"\$\{([^}]+)\}", _repl, raw)
                config = yaml.safe_load(raw) or {}
                logger.info(f"已加载配置文件: {file_path}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败 {file_path}: {e}")
            return {}

    def _load_env_vars(self) -> Dict[str, Any]:
        """加载环境变量"""
        env_vars = {}

        for key, value in os.environ.items():
            if self.env_prefix:
                if key.startswith(self.env_prefix):
                    # 移除前缀并转换为小写
                    config_key = key[len(self.env_prefix):].lower()
                    env_vars[config_key] = self._parse_env_value(value)
            else:
                # 直接使用环境变量名的小写形式
                env_vars[key.lower()] = self._parse_env_value(value)

        return env_vars

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """解析环境变量值"""
        value_lower = value.lower()
        if value_lower in ('true', 'false'):
            return value_lower == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').replace('-', '').isdigit() and '.' in value:
            return float(value)
        else:
            return value

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_override(self, config: Dict[str, Any], env_vars: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        result = config.copy()

        for key, value in env_vars.items():
            # 支持点分隔的键路径，如 database.host
            key_parts = key.split('.')
            current = result

            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[key_parts[-1]] = value

        return result

    def load(self) -> Dict[str, Any]:
        """加载所有配置"""
        # 1. 加载 .env 文件
        self._load_dotenv()

        # 2. 加载环境变量
        env_vars = self._load_env_vars()

        # 3. 加载配置文件（按解析出的候选顺序）
        config = {}
        for path in self._resolve_config_files():
            file_config = self._load_yaml_config(str(path))
            config = self._deep_merge(config, file_config)

        # 4. 应用环境变量覆盖
        final_config = self._apply_env_override(config, env_vars)

        self._config = final_config
        logger.info("配置加载完成")
        return final_config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        current = self._config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def reload(self) -> Dict[str, Any]:
        """重新加载配置"""
        return self.load()

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()


# 便捷函数
def load_config(
    config_files: Optional[List[str]] = None,
    dotenv_files: Optional[List[str]] = None,
    env_prefix: Optional[str] = None
) -> SimpleConfigManager:
    """加载配置的便捷函数"""
    manager = SimpleConfigManager(config_files, dotenv_files, env_prefix)
    manager.load()
    return manager


# 使用示例
if __name__ == "__main__":
    # 加载配置
    config = load_config()

    # 获取配置值
    app_name = config.get("app.app_name", "Default App")
    debug = config.get("app.debug", False)
    port = config.get("app.port", 8000)

    print(f"应用名称: {app_name}")
    print(f"调试模式: {debug}")
    print(f"端口: {port}")

    # 获取API密钥
    ##openai_key = config.get("openai_api_key")
    openai_key = config.get("openai_api_key")
    if openai_key:
        print("OpenAI API Key: 已配置")
    else:
        print("OpenAI API Key: 未配置")