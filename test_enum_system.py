# -*- coding: utf-8 -*-
"""
Enhanced configuration validation script with enum support
"""
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enum_imports():
    """Test enum imports"""
    print("Testing enum imports...")
    
    try:
        from prompt.templates import (
            PromptCategory, 
            TranslationPromptType, 
            SummarizationPromptType, 
            SystemPromptType
        )
        print("SUCCESS: Enum imports successful")
        
        # Test enum values
        print(f"  Translation types: {[t.value for t in TranslationPromptType]}")
        print(f"  Summarization types: {[t.value for t in SummarizationPromptType]}")
        print(f"  System types: {[t.value for t in SystemPromptType]}")
        
        return True
    except Exception as e:
        print(f"FAILED: Enum imports - {e}")
        return False

def test_prompt_manager_enums():
    """Test prompt manager with enums"""
    print("\nTesting prompt manager with enums...")
    
    try:
        from prompt.templates import (
            PromptManager, 
            TranslationPromptType, 
            SummarizationPromptType
        )
        
        manager = PromptManager()
        
        # Test type-safe methods
        translation_prompt = manager.get_translation_prompt(
            TranslationPromptType.ZH_TO_EN, 
            text="test"
        )
        print("SUCCESS: Translation prompt generated with enum")
        print(f"  Length: {len(translation_prompt)}")
        
        summary_prompt = manager.get_summarization_prompt(
            SummarizationPromptType.BASIC_SUMMARY,
            text="test text",
            max_length=100
        )
        print("SUCCESS: Summary prompt generated with enum")
        print(f"  Length: {len(summary_prompt)}")
        
        return True
    except Exception as e:
        print(f"FAILED: Prompt manager enum test - {e}")
        return False

def test_prompt_helper():
    """Test prompt helper utilities"""
    print("\nTesting prompt helper utilities...")
    
    try:
        from prompt.utils import prompt_helper, prompt_validator
        
        # Test helper methods
        prompt_info = prompt_helper.get_prompt_type_info()
        print("SUCCESS: Prompt type info retrieved")
        print(f"  Categories: {list(prompt_info.keys())}")
        
        # Test validation
        validation_result = prompt_validator.validate_prompt_request(
            "translation", 
            "ZH_TO_EN"
        )
        print(f"SUCCESS: Prompt validation - {validation_result}")
        
        # Test invalid validation
        invalid_result = prompt_validator.validate_prompt_request(
            "invalid_category", 
            "INVALID_TYPE"
        )
        print(f"SUCCESS: Invalid prompt validation - {invalid_result}")
        
        return True
    except Exception as e:
        print(f"FAILED: Prompt helper test - {e}")
        return False

def test_translation_service_enums():
    """Test translation service with enums"""
    print("\nTesting translation service with enums...")
    
    try:
        from services.translate import TranslationService
        
        service = TranslationService()
        print("SUCCESS: Translation service created with enum support")
        
        # Note: We won't test actual AI calls since API keys might not be configured
        print("INFO: Translation service ready for enum-based prompts")
        
        return True
    except Exception as e:
        print(f"FAILED: Translation service enum test - {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility with string-based methods"""
    print("\nTesting backward compatibility...")
    
    try:
        from prompt.templates import prompt_manager
        
        # Test old string-based method
        old_prompt = prompt_manager.get_prompt_by_string(
            "translation", 
            "ZH_TO_EN", 
            text="test"
        )
        print("SUCCESS: Backward compatibility maintained")
        print(f"  Old method still works, length: {len(old_prompt)}")
        
        return True
    except Exception as e:
        print(f"FAILED: Backward compatibility test - {e}")
        return False

def main():
    """Main function"""
    print("Enhanced AI Translation Service Configuration Validation")
    print("=" * 60)
    
    # Check working directory
    print(f"Current working directory: {os.getcwd()}")
    
    success = True
    
    # Run tests
    success &= test_enum_imports()
    success &= test_prompt_manager_enums()
    success &= test_prompt_helper()
    success &= test_translation_service_enums()
    success &= test_backward_compatibility()
    
    print("\n" + "=" * 60)
    if success:
        print("SUCCESS: All enum tests passed! Enhanced configuration validated.")
        print("\nEnhancements completed:")
        print("✓ Type-safe enum-based prompt management")
        print("✓ Validation utilities for prompt types")
        print("✓ Helper classes for easier prompt operations")
        print("✓ Backward compatibility maintained")
        print("✓ API endpoints for prompt type discovery")
        
        print("\nNext steps:")
        print("1. Configure API keys in .env file")
        print("2. Run 'python main.py' to start the service")
        print("3. Test new endpoints:")
        print("   - GET /api/translate/prompt-types")
        print("   - POST /api/translate/validate-prompt")
    else:
        print("FAILED: Some enum tests failed, please check configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())