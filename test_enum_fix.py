#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
����ö���޸�
"""
import sys
import os

# �����Ŀ��Ŀ¼��·��
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_feature_code_enum():
    """����FeatureCodeö��"""
    try:
        from schemas.translate import FeatureCode, Feature
        
        print("? FeatureCodeö�ٵ���ɹ�")
        print(f"  - ����ֵ: {[code.value for code in FeatureCode]}")
        
        # ���Դ���Featureʵ��
        features_to_test = [
            (FeatureCode.zh2en, "����Ӣ"),
            (FeatureCode.en2zh, "Ӣ����"),
            (FeatureCode.summarize, "�ܽ�"),
            (FeatureCode.auto_translate, "�Զ�����"),
            (FeatureCode.keyword_summary, "�ؼ����ܽ�"),
            (FeatureCode.structured_summary, "�ṹ���ܽ�"),
        ]
        
        for code, name in features_to_test:
            try:
                feature = Feature(code=code, name=name, description=f"{name}����")
                print(f"  ? {name} ({code.value}) - Feature�����ɹ�")
            except Exception as e:
                print(f"  ? {name} ({code.value}) - Feature����ʧ��: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"? FeatureCodeö�ٲ���ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translate_request():
    """����TranslateRequest"""
    try:
        from schemas.translate import TranslateRequest, FeatureCode
        
        # ���Բ�ͬ��taskֵ
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
                    text="�����ı�",
                    target_language="Ӣ��",
                    task=task
                )
                print(f"  ? {task.value} - TranslateRequest�����ɹ�")
            except Exception as e:
                print(f"  ? {task.value} - TranslateRequest����ʧ��: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"? TranslateRequest����ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_routes():
    """����API·�ɵ���"""
    try:
        from api.translate.routes import router
        print("? API·�ɵ���ɹ�")
        
        # ����features�˵�ĺ���
        from api.translate.routes import list_features
        print("? list_features��������ɹ�")
        
        return True
    except Exception as e:
        print(f"? API·�ɲ���ʧ��: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """�����Ժ���"""
    print("=== ö���޸���֤ ===\n")
    
    print("1. ����FeatureCodeö��...")
    enum_ok = test_feature_code_enum()
    
    print("\n2. ����TranslateRequest...")
    request_ok = test_translate_request()
    
    print("\n3. ����API·��...")
    api_ok = test_api_routes()
    
    print(f"\n=== �����ܽ� ===")
    print(f"ö�ٲ���: {'?' if enum_ok else '?'}")
    print(f"�������: {'?' if request_ok else '?'}")
    print(f"API����: {'?' if api_ok else '?'}")
    
    if enum_ok and request_ok and api_ok:
        print("\n? ö���޸���֤ͨ����")
        return True
    else:
        print("\n? ����������Ҫ�޸�")
        return False

if __name__ == "__main__":
    main()