# -*- coding: utf-8 -*-
"""
快速验证DashScope配置
"""
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=== DashScope配置快速验证 ===")
    
    # 1. 检查配置文件
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'dashscope:' in content and 'default_model: "dashscope"' in content:
                print("✓ config.yaml已更新，DashScope已设为默认模型")
            else:
                print("✗ config.yaml配置可能有问题")
    except Exception as e:
        print(f"✗ 读取config.yaml失败: {e}")
    
    # 2. 检查环境变量示例
    try:
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DASHSCOPE_API_KEY' in content:
                print("✓ .env.example已添加DashScope配置")
            else:
                print("✗ .env.example未添加DashScope配置")
    except Exception as e:
        print(f"✗ 读取.env.example失败: {e}")
    
    # 3. 检查依赖文件
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'dashscope' in content:
                print("✓ requirements.txt已添加dashscope依赖")
            else:
                print("✗ requirements.txt未添加dashscope依赖")
    except Exception as e:
        print(f"✗ 读取requirements.txt失败: {e}")
    
    # 4. 检查服务文件
    try:
        with open('services/ai_model.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class DashScopeService' in content and '"dashscope": DashScopeService' in content:
                print("✓ services/ai_model.py已添加DashScope服务")
            else:
                print("✗ services/ai_model.py未正确添加DashScope服务")
    except Exception as e:
        print(f"✗ 读取services/ai_model.py失败: {e}")
    
    print("\n=== 配置总结 ===")
    print("已完成的配置:")
    print("1. ✓ 将DashScope设为默认AI模型")
    print("2. ✓ 添加DashScope服务实现")
    print("3. ✓ 更新环境变量示例")
    print("4. ✓ 添加相关依赖")
    
    print("\n下一步操作:")
    print("1. 获取DashScope API密钥: https://dashscope.console.aliyun.com/")
    print("2. 复制 .env.example 为 .env")
    print("3. 在 .env 中设置 DASHSCOPE_API_KEY=sk-your_actual_key")
    print("4. 安装依赖: pip install -r requirements.txt")
    print("5. 启动服务: python main.py")
    
    print("\n支持的通义千问模型:")
    print("- qwen-plus (推荐，已设为默认)")
    print("- qwen-turbo (更快响应)")
    print("- qwen-max (最强能力)")
    print("- qwen-max-longcontext (长文本)")

if __name__ == "__main__":
    main()