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

from app.core.simple_config import SimpleConfigManager, load_config
from app.core.config_manager import ConfigManager, create_config_manager


def demo_simple_config():
    """演示简化的配置管理器"""
    print("=== 简化的配置管理器示例 ===")

    # 使用便捷函数加载配置
    config = load_config()

    # 获取配置值
    app_name = config.get("app.app_name", "Default App")
    debug = config.get("app.debug", False)
    port = config.get("app.port", 8000)

    print(f"应用名称: {app_name}")
    print(f"调试模式: {debug}")
    print(f"端口: {port}")

    # 获取API密钥
    openai_key = config.get("openai_api_key")
    if openai_key:
        print("OpenAI API Key: 已配置")
    else:
        print("OpenAI API Key: 未配置")

    # 设置配置值
    config.set("custom.value", "test_value")
    print(f"自定义值: {config.get('custom.value')}")

    print()


def demo_advanced_config():
    """演示通用配置管理器"""
    print("=== 通用配置管理器示例 ===")

    # 创建配置管理器
    config_manager = create_config_manager()

    # 加载配置
    config = config_manager.load()

    # 获取配置值
    app_name = config_manager.get("app.app_name", "Default App")
    debug = config_manager.get("app.debug", False)

    print(f"应用名称: {app_name}")
    print(f"调试模式: {debug}")

    # 获取配置源信息
    sources = config_manager.get_sources()
    print(f"配置源数量: {len(sources)}")
    for source in sources:
        print(f"  - {source.path} ({source.format})")

    # 导出配置
    export_path = "config_export.yaml"
    config_manager.export_to_file(export_path, "yaml")
    print(f"配置已导出到: {export_path}")

    print()


def demo_custom_config():
    """演示自定义配置管理器"""
    print("=== 自定义配置管理器示例 ===")

    # 创建自定义配置管理器
    config_manager = ConfigManager(
        config_paths=["config.yaml", "custom_config.json"],
        dotenv_paths=[".env", ".env.local"],
        env_prefix="MYAPP_",
        auto_reload=False
    )

    # 加载配置
    config = config_manager.load()

    # 获取配置值
    app_name = config_manager.get("app.app_name", "Custom App")
    debug = config_manager.get("app.debug", False)

    print(f"应用名称: {app_name}")
    print(f"调试模式: {debug}")

    print()


def demo_env_override():
    """演示环境变量覆盖"""
    print("=== 环境变量覆盖示例 ===")

    # 设置环境变量
    os.environ["MYAPP_APP_NAME"] = "Environment Override App"
    os.environ["MYAPP_APP_DEBUG"] = "true"

    # 创建配置管理器（带环境变量前缀）
    config_manager = ConfigManager(
        env_prefix="MYAPP_"
    )

    # 加载配置
    config = config_manager.load()

    # 获取配置值（会被环境变量覆盖）
    app_name = config_manager.get("app_name", "Default App")
    debug = config_manager.get("app_debug", False)

    print(f"应用名称 (环境变量覆盖): {app_name}")
    print(f"调试模式 (环境变量覆盖): {debug}")

    # 清理环境变量
    del os.environ["MYAPP_APP_NAME"]
    del os.environ["MYAPP_APP_DEBUG"]

    print()


if __name__ == "__main__":
    print("配置管理器使用示例")
    print("=" * 50)

    try:
        demo_simple_config()
        demo_advanced_config()
        demo_custom_config()
        demo_env_override()

        print("所有示例运行完成！")

    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()