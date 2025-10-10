#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置系统整合验证脚本
"""
import sys
import warnings
from pathlib import Path

def test_unified_config():
    """测试统一配置系统"""
    print("=== 统一配置系统测试 ===")
    
    try:
        from app.core.config import settings
        
        # 基本配置测试
        print(f"✓ 应用名称: {settings.app_name}")
        print(f"✓ 调试模式: {settings.debug}")
        print(f"✓ 端口: {settings.port}")
        print(f"✓ 日志级别: {settings.log_level}")
        
        # 新功能测试
        active_models = settings.get_active_models()
        print(f"✓ 活跃模型: {active_models}")
        
        # 配置验证测试
        is_valid = settings.validate_ai_models()
        print(f"✓ AI模型配置验证: {'通过' if is_valid else '失败'}")
        
        # 配置导出测试
        config_dict = settings.export_config()
        print(f"✓ 配置导出: {len(config_dict)} 个配置项")
        
        return True
        
    except Exception as e:
        print(f"❌ 统一配置系统测试失败: {e}")
        return False


def test_deprecated_warnings():
    """测试废弃警告"""
    print("\n=== 废弃警告测试 ===")
    
    # 捕获警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            from app.core.config_manager import ConfigManager
            from app.core.simple_config import SimpleConfigManager
            
            if len(w) >= 2:
                print("✓ 废弃警告正常显示")
                for warning in w:
                    if "deprecated" in str(warning.message).lower():
                        print(f"  - {warning.message}")
                return True
            else:
                print("❌ 废弃警告未显示")
                return False
                
        except Exception as e:
            print(f"❌ 废弃警告测试失败: {e}")
            return False


def test_main_app_import():
    """测试主应用导入"""
    print("\n=== 主应用导入测试 ===")
    
    try:
        # 测试主应用是否可以正常导入
        from app.main import app
        print("✓ 主应用导入成功")
        
        # 测试核心服务导入
        from app.services.ai_model import AIModelManager
        print("✓ AI模型管理器导入成功")
        
        from app.services.langchain_service import LangChainManager
        print("✓ LangChain服务导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 主应用导入测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("配置系统整合验证")
    print("=" * 50)
    
    tests = [
        test_unified_config,
        test_deprecated_warnings,
        test_main_app_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！配置系统整合成功！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查配置")
        sys.exit(1)


if __name__ == "__main__":
    main()