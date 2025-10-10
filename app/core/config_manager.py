"""
通用配置管理器
支持多种配置格式和高级功能

WARNING: This module is deprecated and will be removed in a future version.
Please use app.core.config instead for new code.
"""
import os
import warnings

warnings.warn(
    "config_manager.py is deprecated. Use app.core.config instead.",
    DeprecationWarning,
    stacklevel=2
)
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from datetime import datetime
import re

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    # Python 3.11+ 提供内置 tomllib
    import tomllib as tomli  # type: ignore
    TOML_AVAILABLE = True
except Exception:
    try:
        import tomli  # type: ignore
        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ConfigSource:
    """配置源信息"""
    path: str
    format: str
    last_modified: Optional[datetime] = None
    priority: int = 0


class ConfigLoader(ABC):
    """配置加载器抽象基类"""

    @abstractmethod
    def load(self, path: str) -> Dict[str, Any]:
        """加载配置文件"""
        pass

    @abstractmethod
    def can_load(self, path: str) -> bool:
        """检查是否可以加载此文件"""
        pass


class YAMLLoader(ConfigLoader):
    """YAML 配置加载器"""

    def can_load(self, path: str) -> bool:
        if not YAML_AVAILABLE:
            return False
        return Path(path).suffix.lower() in ['.yaml', '.yml']

    def load(self, path: str) -> Dict[str, Any]:
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML 未安装")
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
            # 插值 ${VAR} 和 {VAR}
            def _repl_dollar(m: re.Match) -> str:
                var = m.group(1)
                return os.getenv(var, m.group(0))
            
            def _repl_simple(m: re.Match) -> str:
                var = m.group(1)
                return os.getenv(var, m.group(0))
            
            # 先处理 ${VAR} 格式
            raw = re.sub(r"\$\{([^}]+)\}", _repl_dollar, raw)
            # 再处理 {VAR} 格式
            raw = re.sub(r"\{([A-Z_][A-Z0-9_]*)\}", _repl_simple, raw)
            return yaml.safe_load(raw) or {}


class JSONLoader(ConfigLoader):
    """JSON 配置加载器"""

    def can_load(self, path: str) -> bool:
        return Path(path).suffix.lower() == '.json'

    def load(self, path: str) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)


class TOMLLoader(ConfigLoader):
    """TOML 配置加载器"""

    def can_load(self, path: str) -> bool:
        if not TOML_AVAILABLE:
            return False
        return Path(path).suffix.lower() == '.toml'

    def load(self, path: str) -> Dict[str, Any]:
        if not TOML_AVAILABLE:
            raise ImportError("tomli 未安装")

        with open(path, 'rb') as f:
            return tomli.load(f)


class ConfigManager:
    """通用配置管理器"""

    def __init__(
        self,
        config_paths: Optional[List[str]] = None,
        dotenv_paths: Optional[List[str]] = None,
        env_prefix: Optional[str] = None,
        auto_reload: bool = False,
        validation_schema: Optional[Dict[str, Any]] = None
    ):
        """
        初始化配置管理器

        Args:
            config_paths: 配置文件路径列表
            dotenv_paths: .env 文件路径列表
            env_prefix: 环境变量前缀
            auto_reload: 是否自动重新加载
            validation_schema: 验证模式
        """
        self.config_paths = config_paths or ["config.yaml", "config.yml", "config.json"]
        self.dotenv_paths = dotenv_paths or [".env"]
        self.env_prefix = env_prefix
        self.auto_reload = auto_reload
        self.validation_schema = validation_schema

        self._config: Dict[str, Any] = {}
        self._sources: List[ConfigSource] = []
        self._loaders: List[ConfigLoader] = [
            YAMLLoader(),
            JSONLoader(),
            TOMLLoader()
        ]

        # 注册文件监控（如果启用自动重新加载）
        if auto_reload:
            self._file_timestamps: Dict[str, float] = {}

    def _resolve_config_paths(self) -> List[Path]:
        """综合环境与常见约定解析配置路径（保序去重），帮助定位加载失败问题。"""
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
        project_root = here.parents[2]  # .../app/core/config_manager.py -> app -> root
        cwd = Path.cwd()

        # 2) 传入的 config_paths（相对 CWD）
        for name in (self.config_paths or []):
            p = cwd / name
            if str(p) not in seen:
                results.append(p)
                seen.add(str(p))

        # 3) 常见候选
        candidates = [
            cwd / "config.yaml",
            cwd / "config.yml",
            cwd / "config.json",
            cwd / "app" / "config.yaml",
            cwd / "app" / "config.yml",
            cwd / "app" / "config.json",
            project_root / "config.yaml",
            project_root / "config.yml",
            project_root / "config.json",
            project_root / "app" / "config.yaml",
            project_root / "app" / "config.yml",
            project_root / "app" / "config.json",
            Path("/app/config.yaml"),
            Path("/app/app/config.yaml"),
        ]
        for p in candidates:
            if str(p) not in seen:
                results.append(p)
                seen.add(str(p))

        logger.info("ConfigManager 将尝试的配置路径：%s", [str(p) for p in results])
        existing = [p for p in results if p.exists()]
        if not existing:
            logger.warning("ConfigManager 未发现存在的配置文件，请检查 CONFIG_PATH 或文件位置")
        else:
            logger.info("ConfigManager 检测到存在的配置文件：%s", [str(p) for p in existing])
        return existing

    def _load_dotenv_files(self) -> None:
        """加载 .env 文件"""
        if not DOTENV_AVAILABLE:
            logger.warning("python-dotenv 未安装，跳过 .env 文件加载")
            return

        for dotenv_path in self.dotenv_paths:
            path = Path(dotenv_path)
            if path.exists():
                load_dotenv(path)
                logger.info(f"已加载 .env 文件: {dotenv_path}")

    def _load_config_files(self) -> Dict[str, Any]:
        """加载配置文件"""
        config = {}

        for path in self._resolve_config_paths():

            # 找到合适的加载器
            loader = None
            for l in self._loaders:
                if l.can_load(str(path)):
                    loader = l
                    break

            if loader:
                try:
                    file_config = loader.load(str(path))
                    config = self._deep_merge(config, file_config)

                    # 记录配置源
                    self._sources.append(ConfigSource(
                        path=str(path),
                        format=path.suffix[1:],
                        last_modified=datetime.fromtimestamp(path.stat().st_mtime),
                        priority=len(self._sources)
                    ))

                    logger.info(f"已加载配置文件: {path}")
                except Exception as e:
                    logger.error(f"加载配置文件失败 {path}: {e}")
            else:
                logger.warning(f"不支持的配置文件格式: {path}")

        return config

    def _load_env_vars(self) -> Dict[str, Any]:
        """加载环境变量"""
        env_vars = {}

        for key, value in os.environ.items():
            if self.env_prefix and key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower()
                env_vars[config_key] = self._parse_env_value(value)
            elif not self.env_prefix:
                env_vars[key.lower()] = self._parse_env_value(value)

        return env_vars

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool, List, Dict]:
        """解析环境变量值"""
        # 尝试解析为 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        # 解析基本类型
        value_lower = value.lower()
        if value_lower in ('true', 'false'):
            return value_lower == 'true'
        elif value.isdigit():
            return int(value)
        elif (value.replace('.', '', 1).replace('-', '', 1).isdigit() and
              '.' in value):
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
            key_parts = key.split('.')
            current = result

            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[key_parts[-1]] = value

        return result

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置"""
        if not self.validation_schema:
            return

        # 简单的模式验证
        for key, expected_type in self.validation_schema.items():
            if key in config:
                if not isinstance(config[key], expected_type):
                    logger.warning(f"配置项 {key} 类型不匹配，期望 {expected_type}")

    def _check_file_changes(self) -> bool:
        """检查文件是否发生变化"""
        if not self.auto_reload:
            return False

        changed = False
        for source in self._sources:
            path = Path(source.path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                if source.path not in self._file_timestamps:
                    self._file_timestamps[source.path] = current_mtime
                elif self._file_timestamps[source.path] != current_mtime:
                    changed = True
                    self._file_timestamps[source.path] = current_mtime

        return changed

    def load(self) -> Dict[str, Any]:
        """加载所有配置"""
        # 1. 加载 .env 文件
        self._load_dotenv_files()

        # 2. 加载环境变量
        env_vars = self._load_env_vars()

        # 3. 加载配置文件
        config = self._load_config_files()

        # 4. 应用环境变量覆盖
        final_config = self._apply_env_override(config, env_vars)

        # 5. 验证配置
        self._validate_config(final_config)

        self._config = final_config
        logger.info("配置加载完成")
        return final_config

    def reload(self) -> Dict[str, Any]:
        """重新加载配置"""
        self._sources.clear()
        return self.load()

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

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def get_sources(self) -> List[ConfigSource]:
        """获取配置源信息"""
        return self._sources.copy()

    def export_to_file(self, path: str, format: str = 'yaml') -> None:
        """导出配置到文件"""
        if format.lower() == 'yaml':
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML 未安装")
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
        elif format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def watch_changes(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """监听配置变化"""
        if not self.auto_reload:
            logger.warning("自动重新加载未启用，无法监听变化")
            return

        import time
        while True:
            if self._check_file_changes():
                logger.info("检测到配置文件变化，正在重新加载...")
                old_config = self._config.copy()
                new_config = self.reload()
                if new_config != old_config:
                    callback(new_config)
            time.sleep(1)  # 检查间隔


# 便捷函数
def create_config_manager(
    config_paths: Optional[List[str]] = None,
    dotenv_paths: Optional[List[str]] = None,
    env_prefix: Optional[str] = None,
    auto_reload: bool = False
) -> ConfigManager:
    """创建配置管理器的便捷函数"""
    return ConfigManager(config_paths, dotenv_paths, env_prefix, auto_reload)


# 使用示例
if __name__ == "__main__":
    # 创建配置管理器
    config_manager = create_config_manager()

    # 加载配置
    config = config_manager.load()

    # 获取配置值
    app_name = config_manager.get("app.app_name", "Default App")
    debug = config_manager.get("app.debug", False)

    print(f"应用名称: {app_name}")
    print(f"调试模式: {debug}")

    # 导出配置
    config_manager.export_to_file("config_export.yaml", "yaml")