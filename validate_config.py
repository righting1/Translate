# -*- coding: utf-8 -*-
"""
Simple configuration validation script
"""
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import yaml
        print("SUCCESS: yaml import")
    except ImportError as e:
        print(f"FAILED: yaml import - {e}")
        return False
    
    try:
        from pathlib import Path
        print("SUCCESS: pathlib import")
    except ImportError as e:
        print(f"FAILED: pathlib import - {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("SUCCESS: pydantic import")
    except ImportError as e:
        print(f"FAILED: pydantic import - {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        from core.config import settings
        print("SUCCESS: Configuration loaded")
        print(f"  App name: {settings.app_name}")
        print(f"  Port: {settings.port}")
        print(f"  AI model config: {'Configured' if settings.ai_model else 'Not configured'}")
        
        if settings.ai_model:
            print(f"  Default model: {settings.ai_model.get('default_model', 'None')}")
        
        return True
    except Exception as e:
        print(f"FAILED: Configuration loading - {e}")
        return False

def test_prompt_templates():
    """Test prompt templates"""
    print("\nTesting prompt templates...")
    
    try:
        from prompt.templates import PromptManager
        manager = PromptManager()
        print("SUCCESS: Prompt manager created")
        
        # Test prompt generation
        prompt = manager.get_prompt("translation", "ZH_TO_EN", text="test")
        print(f"SUCCESS: Prompt template generated, length: {len(prompt)}")
        
        return True
    except Exception as e:
        print(f"FAILED: Prompt template test - {e}")
        return False

def test_translation_service():
    """Test translation service"""
    print("\nTesting translation service...")
    
    try:
        from services.translate import TranslationService
        service = TranslationService()
        print("SUCCESS: Translation service created")
        
        return True
    except Exception as e:
        print(f"FAILED: Translation service test - {e}")
        return False

def check_config_file():
    """Check configuration file"""
    print("\nChecking configuration file...")
    
    from pathlib import Path
    config_path = Path("config.yaml")
    if config_path.exists():
        print("SUCCESS: config.yaml file exists")
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'ai_model' in config:
                print("SUCCESS: AI model config exists")
                ai_config = config['ai_model']
                print(f"  Default model: {ai_config.get('default_model', 'None')}")
                
                # Check model configurations
                models = ['openai', 'zhipuai', 'ollama', 'azure_openai']
                for model in models:
                    if model in ai_config:
                        print(f"  {model}: configured")
                    else:
                        print(f"  {model}: not configured")
            else:
                print("WARNING: AI model config not found")
                
        except Exception as e:
            print(f"FAILED: Config file parsing - {e}")
    else:
        print("FAILED: config.yaml file not found")

def main():
    """Main function"""
    print("AI Translation Service Configuration Validation")
    print("=" * 50)
    
    # Check working directory
    print(f"Current working directory: {os.getcwd()}")
    
    success = True
    
    # Run tests
    success &= test_basic_imports()
    check_config_file()
    success &= test_config_loading()
    success &= test_prompt_templates()
    success &= test_translation_service()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: All tests passed! Configuration validation successful.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure API keys")
        print("2. Run 'python main.py' to start the service")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("FAILED: Some tests failed, please check configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())