#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple configuration validation script
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import yaml
        print("✓ yaml import success")
    except ImportError as e:
        print(f"✗ yaml import failed: {e}")
        return False
    
    try:
        from pathlib import Path
        print("✓ pathlib import success")
    except ImportError as e:
        print(f"✗ pathlib import failed: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✓ pydantic import success")
    except ImportError as e:
        print(f"✗ pydantic import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    try:
        from core.config import settings
        print(f"✓ 配置加载成功")
        print(f"  应用名称: {settings.app_name}")
        print(f"  端口: {settings.port}")
        print(f"  AI模型配置: {'已配置' if settings.ai_model else '未配置'}")
        
        if settings.ai_model:
            print(f"  默认模型: {settings.ai_model.get('default_model', 'None')}")
        
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_prompt_templates():
    """测试提示词模板"""
    print("\n测试提示词模板...")
    
    try:
        from prompt.templates import PromptManager
        manager = PromptManager()
        print("✓ 提示词管理器创建成功")
        
        # 测试获取提示词
        prompt = manager.get_prompt("translation", "ZH_TO_EN", text="测试")
        print(f"✓ 提示词模板生成成功，长度: {len(prompt)}")
        
        return True
    except Exception as e:
        print(f"✗ 提示词模板测试失败: {e}")
        return False

def test_translation_service():
    """测试翻译服务"""
    print("\n测试翻译服务...")
    
    try:
        from services.translate import TranslationService
        service = TranslationService()
        print("✓ 翻译服务创建成功")
        
        return True
    except Exception as e:
        print(f"✗ 翻译服务测试失败: {e}")
        return False

def check_config_file():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    config_path = Path("config.yaml")
    if config_path.exists():
        print("✓ config.yaml 文件存在")
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'ai_model' in config:
                print("✓ AI模型配置存在")
                ai_config = config['ai_model']
                print(f"  默认模型: {ai_config.get('default_model', 'None')}")
                
                # 检查各个模型配置
                models = ['openai', 'zhipuai', 'ollama', 'azure_openai']
                for model in models:
                    if model in ai_config:
                        print(f"  {model}: 已配置")
                    else:
                        print(f"  {model}: 未配置")
            else:
                print("⚠ AI模型配置不存在")
                
        except Exception as e:
            print(f"✗ 配置文件解析失败: {e}")
    else:
        print("✗ config.yaml 文件不存在")

def main():
    """主函数"""
    print("🔍 AI大模型翻译服务配置验证")
    print("=" * 50)
    
    # 检查工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    success = True
    
    # 运行各种测试
    success &= test_basic_imports()
    check_config_file()
    success &= test_config_loading()
    success &= test_prompt_templates()
    success &= test_translation_service()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试通过！配置验证成功。")
        print("\n下一步:")
        print("1. 复制 .env.example 为 .env 并配置API密钥")
        print("2. 运行 python main.py 启动服务")
        print("3. 访问 http://localhost:8000/docs 查看API文档")
    else:
        print("❌ 部分测试失败，请检查配置。")
    
    return 0 if success else 1

if __name__ == "__main__":
    from pathlib import Path
    exit(main())