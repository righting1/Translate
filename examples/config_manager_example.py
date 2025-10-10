# -*- coding: utf-8 -*-
"""
配置管理器使用示例
演示如何使用简化的配置管理器和通用配置管理器
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def demo_unified_config():
    """演示统一的配置系统"""
    print("=== 统一配置系统示例 ===")

    # 直接使用主配置系统
    print(f"应用名称: {settings.app_name}")
    print(f"调试模式: {settings.debug}")
    print(f"端口: {settings.port}")
    print(f"主机: {settings.host}")
    print(f"日志级别: {settings.log_level}")

    # 检查AI模型配置
    if settings.ai_model:
        print("\nAI模型配置:")
        print(f"默认模型: {settings.ai_model.get('default_model', 'N/A')}")
        
        # 显示可用的模型服务
        available_models = []
        for key, value in settings.ai_model.items():
            if key != 'default_model' and isinstance(value, dict):
                available_models.append(key)
        print(f"可用模型: {', '.join(available_models)}")
    else:
        print("\nAI模型配置: 未配置")

    # 检查环境变量配置
    print(f"\n其他配置:")
    print(f"数据库URL: {'已配置' if settings.database_url else '未配置'}")
    print(f"JWT密钥: {'已配置' if settings.jwt_secret_key else '未配置'}")
    print(f"Redis URL: {'已配置' if settings.redis_url else '未配置'}")

    print()


def demo_legacy_config():
    """演示废弃的配置管理器（带警告）"""
    print("=== 废弃配置管理器示例（将显示警告）===")
    
    try:
        # 这将触发废弃警告
        from app.core.config_manager import ConfigManager, create_config_manager
        
        # 创建配置管理器
        config_manager = create_config_manager()
        
        # 加载配置
        config = config_manager.load()
        
        # 获取配置值
        app_name = config_manager.get("app.app_name", "Default App")
        debug = config_manager.get("app.debug", False)
        
        print(f"应用名称: {app_name}")
        print(f"调试模式: {debug}")
        
        print("注意：上面应该显示了废弃警告")
        
    except Exception as e:
        print(f"废弃配置管理器示例失败（这是预期的）: {e}")
    
    print()


def demo_config_comparison():
    """演示新旧配置系统的对比"""
    print("=== 配置系统对比 ===")
    
    print("✅ 新的统一配置系统优势:")
    print("  - 基于 Pydantic，有类型验证")
    print("  - 与 FastAPI 无缝集成")
    print("  - 支持环境变量插值")
    print("  - 配置结构清晰")
    print("  - 性能更好")
    
    print("\n❌ 旧配置系统问题:")
    print("  - 多个重复的配置系统")
    print("  - 没有类型检查")
    print("  - 维护复杂")
    print("  - 功能重叠")
    
    print()


if __name__ == "__main__":
    print("配置管理器使用示例")
    print("=" * 50)

    try:
        demo_unified_config()
        demo_legacy_config()
        demo_config_comparison()

        print("所有示例运行完成！")

    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()