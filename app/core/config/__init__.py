import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseModel):
    app_name: str
    debug: bool
    host: str
    port: int
    reload: bool
    log_level: str
    version: str
    ai_model: Optional[Dict[str, Any]] = None

    # 新增的环境变量配置
    # openai_api_key: Optional[str] = None
    # openai_base_url: Optional[str] = None
    # zhipuai_api_key: Optional[str] = None
    # dashscope_api_key: Optional[str] = None
    database_url: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    redis_url: Optional[str] = None

    @classmethod
    def load_from_env_and_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """只从环境变量获取通用配置，AI模型配置只从 YAML 文件加载"""

        env_config = {
            "app_name": os.getenv("APP_NAME", "Translate API"),
            "debug": os.getenv("DEBUG", "true").lower() == "true",
            "host": os.getenv("HOST", "127.0.0.1"),
            "port": int(os.getenv("PORT", "8000")),
            "reload": os.getenv("RELOAD", "true").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "info"),
            "version": os.getenv("VERSION", "0.1.0"),
            # "openai_api_key": os.getenv("OPENAI_API_KEY"),
            # "openai_base_url": os.getenv("OPENAI_BASE_URL"),
            # "zhipuai_api_key": os.getenv("ZHIPUAI_API_KEY"),
            # "dashscope_api_key": os.getenv("DASHSCOPE_API_KEY"),
            "database_url": os.getenv("DATABASE_URL"),
            "jwt_secret_key": os.getenv("JWT_SECRET_KEY"),
            "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "jwt_access_token_expire_minutes": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "redis_url": os.getenv("REDIS_URL"),
        }

        config_file = Path(config_path)

        # 如果YAML文件存在，从中加载额外配置
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    # 替换环境变量
                    config_content = cls._replace_env_vars(config_content)
                    config_data = yaml.safe_load(config_content) or {}

                # 合并YAML配置（YAML中的配置会覆盖环境变量）
                if 'app' in config_data:
                    for key, value in config_data['app'].items():
                        if key in env_config:
                            env_config[key] = value

                # 添加AI模型配置
                if 'ai_model' in config_data:
                    env_config['ai_model'] = config_data['ai_model']

            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

        return cls(**env_config)

    @staticmethod
    def _replace_env_vars(content: str) -> str:
        """替换配置文件中的环境变量"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, f"${{{var_name}}}")  # 如果环境变量不存在，保持原样
        
        # 匹配 ${VAR_NAME} 格式的环境变量
        return re.sub(r'\$\{([^}]+)\}', replace_var, content)

    @classmethod
    def load_from_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """从 YAML 文件加载配置"""
        # 默认配置
        default_config = {
            "app_name": "Translate API",
            "debug": True,
            "host": "127.0.0.1",
            "port": 8000,
            "reload": True,
            "log_level": "info",
            "version": "0.1.0"
        }

        config_file = Path(config_path)

        if not config_file.exists():
            # 如果配置文件不存在，返回默认配置
            return cls(**default_config)

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
                # 替换环境变量
                config_content = cls._replace_env_vars(config_content)
                config_data = yaml.safe_load(config_content) or {}

            # 提取应用配置部分，与默认配置合并
            app_config = config_data.get('app', {})
            merged_config = {**default_config, **app_config}

            # 添加AI模型配置
            if 'ai_model' in config_data:
                merged_config['ai_model'] = config_data['ai_model']

            return cls(**merged_config)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return cls(**default_config)

    @staticmethod
    def _replace_env_vars(content: str) -> str:
        """替换配置文件中的环境变量"""
        import re

        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, f"${{{var_name}}}")  # 如果环境变量不存在，保持原样

        # 匹配 ${VAR_NAME} 格式的环境变量
        return re.sub(r'\$\{([^}]+)\}', replace_var, content)


def _yaml_has_models(p: Path) -> bool:
    try:
        if not p.exists():
            return False
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        ai = data.get("ai_model") or {}
        models = ai.get("models") or []
        return isinstance(models, list) and len(models) > 0
    except Exception:
        return False


def _resolve_config_path() -> str:
    """解析配置文件的绝对路径。
    优先级：
    1) 显式环境变量 CONFIG_PATH（存在即用）
    2) 在常见候选路径中优先选择包含 ai_model.models 的文件
    3) 若都不含模型，则选择第一个存在的文件
    4) 兜底返回 CWD/config.yaml 的绝对路径
    """
    env_path = os.getenv("CONFIG_PATH")
    if env_path:
        p = Path(env_path).expanduser()
        chosen = str(p.resolve())
        logger.info(f"CONFIG_PATH provided, using: {chosen}")
        return chosen

    here = Path(__file__).resolve()
    candidates = [
        Path.cwd() / "config.yaml",          # 当前工作目录
        here.parents[3] / "config.yaml",     # 项目根目录
        here.parents[2] / "config.yaml",     # app/config.yaml（相对源码位置）
        Path.cwd() / "app" / "config.yaml", # 工作目录下 app/config.yaml
        Path("/app/config.yaml"),            # Docker 常用路径
    ]

    # 先找含模型列表的配置
    for p in candidates:
        try:
            if _yaml_has_models(p):
                chosen = str(p.resolve())
                logger.info(f"Using config with models: {chosen}")
                return chosen
        except Exception:
            continue

    # 再退而求其次，找第一个存在的
    for p in candidates:
        try:
            if p.exists():
                chosen = str(p.resolve())
                logger.info(f"Using first existing config (no models found): {chosen}")
                return chosen
        except Exception:
            continue

    # 兜底
    fallback = str((Path.cwd() / "config.yaml").resolve())
    logger.warning(f"No config.yaml found, fallback to: {fallback}")
    return fallback





# 使用解析到的绝对路径加载配置
_CONFIG_ABS_PATH = _resolve_config_path()
logger.info(f"Using config path: {_CONFIG_ABS_PATH}")
settings = Settings.load_from_env_and_yaml(_CONFIG_ABS_PATH)
if not settings.ai_model or not settings.ai_model.get("models"):
    logger.warning("ai_model.models not found in loaded config. Check file path/content.")


