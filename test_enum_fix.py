#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试枚举修复
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_feature_code_enum():
    """测试FeatureCode枚举"""
    try:
        from schemas.translate import FeatureCode, Feature
        
        print("? FeatureCode枚举导入成功")
        print(f"  - 可用值: {[code.value for code in FeatureCode]}")
        
        # 测试创建Feature实例
        features_to_test = [
            (FeatureCode.zh2en, "中译英"),
            (FeatureCode.en2zh, "英译中"),
            (FeatureCode.summarize, "总结"),
            (FeatureCode.auto_translate, "自动翻译"),
            (FeatureCode.keyword_summary, "关键词总结"),
            (FeatureCode.structured_summary, "结构化总结"),
        ]
        
        for code, name in features_to_test:
            try:
                feature = Feature(code=code, name=name, description=f"{name}功能")
                print(f"  ? {name} ({code.value}) - Feature创建成功")
            except Exception as e:
                print(f"  ? {name} ({code.value}) - Feature创建失败: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"? FeatureCode枚举测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translate_request():
    """测试TranslateRequest"""
    try:
        from schemas.translate import TranslateRequest, FeatureCode
        
        # 测试不同的task值
        tasks_to_test = [
            FeatureCode.zh2en,
            FeatureCode.en2zh,
            FeatureCode.summarize,
            FeatureCode.auto_translate,
            FeatureCode.keyword_summary,
            FeatureCode.structured_summary,
        ]
        
        for task in tasks_to_test:
            try:
                request = TranslateRequest(
                    text="测试文本",
                    target_language="英文",
                    task=task
                )
                print(f"  ? {task.value} - TranslateRequest创建成功")
            except Exception as e:
                print(f"  ? {task.value} - TranslateRequest创建失败: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"? TranslateRequest测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_routes():
    """测试API路由导入"""
    try:
        from api.translate.routes import router
        print("? API路由导入成功")
        
        # 测试features端点的函数
        from api.translate.routes import list_features
        print("? list_features函数导入成功")
        
        return True
    except Exception as e:
        print(f"? API路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== 枚举修复验证 ===\n")
    
    print("1. 测试FeatureCode枚举...")
    enum_ok = test_feature_code_enum()
    
    print("\n2. 测试TranslateRequest...")
    request_ok = test_translate_request()
    
    print("\n3. 测试API路由...")
    api_ok = test_api_routes()
    
    print(f"\n=== 测试总结 ===")
    print(f"枚举测试: {'?' if enum_ok else '?'}")
    print(f"请求测试: {'?' if request_ok else '?'}")
    print(f"API测试: {'?' if api_ok else '?'}")
    
    if enum_ok and request_ok and api_ok:
        print("\n? 枚举修复验证通过！")
        return True
    else:
        print("\n? 还有问题需要修复")
        return False

if __name__ == "__main__":
    main()