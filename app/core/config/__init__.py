import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()


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
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    zhipuai_api_key: Optional[str] = None
    dashscope_api_key: Optional[str] = None
    database_url: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    redis_url: Optional[str] = None

    @classmethod
    def load_from_env_and_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """从环境变量和 YAML 文件加载配置，环境变量优先"""
        # 从环境变量获取配置
        env_config = {
            "app_name": os.getenv("APP_NAME", "Translate API"),
            "debug": os.getenv("DEBUG", "true").lower() == "true",
            "host": os.getenv("HOST", "127.0.0.1"),
            "port": int(os.getenv("PORT", "8000")),
            "reload": os.getenv("RELOAD", "true").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "info"),
            "version": os.getenv("VERSION", "0.1.0"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "openai_base_url": os.getenv("OPENAI_BASE_URL"),
            "zhipuai_api_key": os.getenv("ZHIPUAI_API_KEY"),
            "dashscope_api_key": os.getenv("DASHSCOPE_API_KEY"),
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
                print(f"加载配置文件失败: {e}")

        return cls(**env_config)
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
            print(f"加载配置文件失败: {e}")
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


settings = Settings.load_from_env_and_yaml("config.yaml")


