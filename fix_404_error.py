#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain 404错误诊断和修复脚本
"""
import logging
import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_langchain_service():
    """测试 LangChain 服务并诊断 404 错误"""
    logger.info("=== 开始 LangChain 服务诊断 ===")
    
    try:
        # 1. 导入配置
        from core.config import settings
        logger.info("? 配置文件导入成功")
        
        # 2. 检查配置
        if hasattr(settings, 'ai_model') and settings.ai_model:
            logger.info(f"? AI模型配置存在: {list(settings.ai_model.keys())}")
            default_model = settings.ai_model.get('default_model', 'None')
            logger.info(f"默认模型: {default_model}")
            
            # 检查具体配置
            if default_model in settings.ai_model:
                config = settings.ai_model[default_model]
                logger.info(f"默认模型配置:")
                logger.info(f"  - 服务类型: {config.get('service_type')}")
                logger.info(f"  - 模型名称: {config.get('model')}")
                logger.info(f"  - 基础URL: {config.get('base_url')}")
                logger.info(f"  - API密钥: {'***已设置***' if config.get('api_key') else '未设置'}")
        else:
            logger.error("? AI模型配置不存在")
            return False
        
        # 3. 创建服务
        from services.langchain_service import LangChainManager
        manager = LangChainManager()
        logger.info("? LangChain管理器创建成功")
        
        # 4. 获取默认服务
        service = manager.get_default_service()
        if service:
            logger.info("? 获取默认服务成功")
            logger.info(f"服务信息:")
            logger.info(f"  - 类型: {type(service).__name__}")
            logger.info(f"  - 模型名: {service.model_name}")
            logger.info(f"  - 服务类型: {service.service_type}")
            logger.info(f"  - LLM对象: {type(service.llm).__name__ if service.llm else 'None'}")
            
            # 5. 检查 LLM 初始化
            if service.llm is None:
                logger.error("? self.llm 为 None，尝试重新初始化...")
                service._initialize_llm()
                if service.llm:
                    logger.info("? 重新初始化成功")
                else:
                    logger.error("? 重新初始化失败")
                    return False
            
            # 6. 测试文本生成
            logger.info("开始测试文本生成...")
            test_prompt = "Say hello"
            
            try:
                result = await service.generate_text(test_prompt)
                logger.info(f"? 文本生成成功: {result[:100]}...")
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"? 文本生成失败: {error_msg}")
                
                # 404 错误诊断
                if "404" in error_msg:
                    logger.error("? 发现 404 错误!")
                    logger.error("可能的原因:")
                    logger.error("1. API端点URL不正确")
                    logger.error("2. 模型名称不存在")
                    logger.error("3. 服务不可用")
                    
                    # 修复建议
                    logger.info("? 修复建议:")
                    if service.service_type == "dashscope":
                        logger.info("DashScope 正确配置:")
                        logger.info("  base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1'")
                        logger.info("  model: 'qwen-turbo' 或 'qwen-plus'")
                    elif service.service_type == "openai":
                        logger.info("OpenAI 正确配置:")
                        logger.info("  base_url: 不设置（使用默认）或正确的代理URL")
                        logger.info("  model: 'gpt-3.5-turbo' 或其他有效模型")
                        
                return False
                
        else:
            logger.error("? 获取默认服务失败")
            return False
            
    except Exception as e:
        logger.error(f"? 测试过程中出现异常: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def provide_fix_recommendations():
    """提供修复建议"""
    logger.info("=== 修复建议 ===")
    
    logger.info("1. 检查 config.yaml 配置:")
    logger.info("""
ai_model:
  default_model: "dashscope"  # 或 "openai"
  dashscope:
    service_type: "dashscope"
    model: "qwen-turbo"
    api_key: "your_dashscope_api_key"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    temperature: 0.7
    max_tokens: 2000
""")
    
    logger.info("2. 设置环境变量:")
    logger.info("   PowerShell: $env:DASHSCOPE_API_KEY='your_api_key'")
    logger.info("   CMD: set DASHSCOPE_API_KEY=your_api_key")
    
    logger.info("3. 常见 404 错误解决:")
    logger.info("   - 确保 base_url 正确")
    logger.info("   - 检查模型名称是否有效")
    logger.info("   - 验证 API 服务状态")

async def main():
    """主函数"""
    logger.info("开始 LangChain 404 错误诊断...")
    
    success = await test_langchain_service()
    
    if not success:
        provide_fix_recommendations()
    
    logger.info("=== 诊断完成 ===")

if __name__ == "__main__":
    asyncio.run(main())