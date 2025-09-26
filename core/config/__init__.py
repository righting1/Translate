import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str
    debug: bool
    host: str
    port: int
    reload: bool
    log_level: str
    version: str
    ai_model: Optional[Dict[str, Any]] = None

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


settings = Settings.load_from_yaml()


