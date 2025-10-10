#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
���Ի���������ֵ����
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("=== ����������ֵ���ܲ��� ===")
    
    # ���� .env �ļ�
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("? .env �ļ����سɹ�")
    except ImportError:
        print("? python-dotenv δ��װ")
        return
    except Exception as e:
        print(f"? ���� .env �ļ�ʧ��: {e}")
        return
    
    # ���һЩ�ؼ���������
    print("\n=== ����������� ===")
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
            # ����������Ϣ��ֻ��ʾǰ�����ַ�
            if "API_KEY" in var and len(value) > 10:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            print(f"? {var}: {display_value}")
        else:
            print(f"? {var}: δ����")
    
    # ���� ConfigManager
    print("\n=== ConfigManager ��ֵ���� ===")
    try:
        from app.core.config_manager import ConfigManager
        
        # �������ù�����
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"? ���ü��سɹ�")
        print(f"? �������ü�: {list(config.keys())}")
        
        # ���Ӧ������
        if 'app' in config:
            app_config = config['app']
            print(f"\n? Ӧ������:")
            for key, value in app_config.items():
                print(f"  {key}: {value}")
        
        # ���AI��������
        if 'ai_services' in config:
            ai_services = config['ai_services']
            print(f"\n? AI��������:")
            print(f"  Ĭ�Ϸ���: {ai_services.get('default', 'N/A')}")
            
            # ���������������
            for service_name in ['dashscope', 'openai', 'zhipuai']:
                if service_name in ai_services:
                    service_config = ai_services[service_name]
                    print(f"\n  {service_name.upper()} ����:")
                    for key, value in service_config.items():
                        # ��API��Կ����������ʾ
                        if key == 'api_key' and isinstance(value, str) and len(value) > 10:
                            display_value = value[:8] + "..." + value[-4:]
                        else:
                            display_value = value
                        print(f"    {key}: {display_value}")
        
        # ����Ƿ���δ�滻��ռλ��
        print(f"\n? ���δ�滻��ռλ��:")
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
                # ���� {VAR} ��ʽ��ռλ��
                matches = re.findall(r'\{([A-Z_][A-Z0-9_]*)\}', obj)
                for match in matches:
                    placeholders.append(f"{path}: {{{match}}}")
            return placeholders
        
        placeholders = find_placeholders(config)
        if placeholders:
            print("? ����δ�滻��ռλ��:")
            for placeholder in placeholders:
                print(f"  {placeholder}")
        else:
            print("? ����ռλ��������ȷ�滻")
            
    except Exception as e:
        print(f"? ConfigManager ����ʧ��: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()