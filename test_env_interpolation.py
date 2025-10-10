#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境变量插值功能
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("=== 环境变量插值功能测试 ===")
    
    # 加载 .env 文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("? .env 文件加载成功")
    except ImportError:
        print("? python-dotenv 未安装")
        return
    except Exception as e:
        print(f"? 加载 .env 文件失败: {e}")
        return
    
    # 检查一些关键环境变量
    print("\n=== 环境变量检查 ===")
    key_vars = [
        "APP_NAME", "DEBUG", "HOST", "PORT",
        "OPENAI_API_KEY", "OPENAI_MODEL",
        "DASHSCOPE_API_KEY", "DASHSCOPE_MODEL",
        "ZHIPUAI_API_KEY", "ZHIPUAI_MODEL",
        "DEFAULT_AI_SERVICE"
    ]
    
    for var in key_vars:
        value = os.getenv(var)
        if value:
            # 对于敏感信息，只显示前几个字符
            if "API_KEY" in var and len(value) > 10:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            print(f"? {var}: {display_value}")
        else:
            print(f"? {var}: 未设置")
    
    # 测试 ConfigManager
    print("\n=== ConfigManager 插值测试 ===")
    try:
        from app.core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"? 配置加载成功")
        print(f"? 顶级配置键: {list(config.keys())}")
        
        # 检查应用配置
        if 'app' in config:
            app_config = config['app']
            print(f"\n? 应用配置:")
            for key, value in app_config.items():
                print(f"  {key}: {value}")
        
        # 检查AI服务配置
        if 'ai_services' in config:
            ai_services = config['ai_services']
            print(f"\n? AI服务配置:")
            print(f"  默认服务: {ai_services.get('default', 'N/A')}")
            
            # 检查各个服务的配置
            for service_name in ['dashscope', 'openai', 'zhipuai']:
                if service_name in ai_services:
                    service_config = ai_services[service_name]
                    print(f"\n  {service_name.upper()} 配置:")
                    for key, value in service_config.items():
                        # 对API密钥进行脱敏显示
                        if key == 'api_key' and isinstance(value, str) and len(value) > 10:
                            display_value = value[:8] + "..." + value[-4:]
                        else:
                            display_value = value
                        print(f"    {key}: {display_value}")
        
        # 检查是否还有未替换的占位符
        print(f"\n? 检查未替换的占位符:")
        def find_placeholders(obj, path=""):
            placeholders = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    placeholders.extend(find_placeholders(value, f"{path}.{key}" if path else key))
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    placeholders.extend(find_placeholders(value, f"{path}[{i}]"))
            elif isinstance(obj, str):
                import re
                # 查找 {VAR} 格式的占位符
                matches = re.findall(r'\{([A-Z_][A-Z0-9_]*)\}', obj)
                for match in matches:
                    placeholders.append(f"{path}: {{{match}}}")
            return placeholders
        
        placeholders = find_placeholders(config)
        if placeholders:
            print("? 发现未替换的占位符:")
            for placeholder in placeholders:
                print(f"  {placeholder}")
        else:
            print("? 所有占位符都已正确替换")
            
    except Exception as e:
        print(f"? ConfigManager 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()