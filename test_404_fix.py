#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的 LangChain 服务，验证 404 错误是否解决
"""
import logging
import sys
import os
import asyncio

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_fixed_service():
    """测试修复后的服务"""
    logger.info("=== 测试修复后的 LangChain 服务 ===")
    
    try:
        # 导入服务
        from services.langchain_service import LangChainManager
        from core.config import settings
        
        # 检查配置
        logger.info("? 检查配置:")
        logger.info(f"默认模型: {settings.ai_model.get('default_model')}")
        
        dashscope_config = settings.ai_model.get('dashscope', {})
        logger.info(f"DashScope 配置:")
        logger.info(f"  - 服务类型: {dashscope_config.get('service_type')}")
        logger.info(f"  - 基础URL: {dashscope_config.get('base_url')}")
        logger.info(f"  - 模型: {dashscope_config.get('model')}")
        logger.info(f"  - API密钥: {'***已设置***' if dashscope_config.get('api_key') else '未设置'}")
        
        # 创建管理器
        logger.info("? 创建 LangChain 管理器...")
        manager = LangChainManager()
        
        # 获取服务
        logger.info("? 获取默认服务...")
        service = manager.get_default_service()
        
        if not service:
            logger.error("? 无法获取默认服务")
            return False
            
        if service.llm is None:
            logger.error("? service.llm 为 None")
            return False
            
        logger.info(f"? 服务创建成功: {type(service.llm).__name__}")
        
        # 测试简单的文本生成
        logger.info("? 开始测试文本生成...")
        test_prompt = "请说 Hello"
        
        try:
            result = await service.generate_text(test_prompt)
            logger.info(f"? 文本生成成功!")
            logger.info(f"? 响应: {result}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"? 文本生成失败: {error_msg}")
            
            if "404" in error_msg:
                logger.error("? 仍然存在 404 错误")
                logger.info("请检查:")
                logger.info("1. API 密钥是否正确")
                logger.info("2. 网络连接是否正常") 
                logger.info("3. DashScope 服务是否可用")
            elif "401" in error_msg:
                logger.error("? 认证失败 - API 密钥问题")
            
            return False
            
    except Exception as e:
        logger.error(f"? 测试过程出现异常: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

async def test_chain_execution():
    """测试链执行"""
    logger.info("=== 测试 Chain 执行 ===")
    
    try:
        from services.langchain_translate import LangChainTranslationService
        
        # 创建翻译服务
        logger.info("? 创建 LangChain 翻译服务...")
        translate_service = LangChainTranslationService(use_chains=False)  # 先不使用链
        
        # 测试简单翻译
        logger.info("? 测试中英文翻译...")
        
        # 测试中文到英文
        zh_text = "你好，世界"
        logger.info(f"翻译文本: {zh_text}")
        
        result = await translate_service.zh2en(zh_text)
        logger.info(f"? 中英翻译成功: {result}")
        
        # 测试英文到中文
        en_text = "Hello, world"
        logger.info(f"翻译文本: {en_text}")
        
        result = await translate_service.en2zh(en_text)
        logger.info(f"? 英中翻译成功: {result}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"? 链执行测试失败: {error_msg}")
        
        if "404" in error_msg:
            logger.error("? 链执行中发现 404 错误")
            logger.info("这可能是配置传递问题")
        
        return False

async def main():
    """主函数"""
    logger.info("? 开始 404 错误修复验证...")
    
    # 测试基础服务
    basic_ok = await test_fixed_service()
    
    if basic_ok:
        logger.info("? 基础服务测试通过")
        
        # 测试链执行
        chain_ok = await test_chain_execution()
        
        if chain_ok:
            logger.info("? 所有测试通过！404 错误已修复")
        else:
            logger.warning("?? 链执行测试失败，但基础服务正常")
    else:
        logger.error("? 基础服务测试失败")
        
        logger.info("? 修复建议:")
        logger.info("1. 检查 config.yaml 中的 base_url 是否为:")
        logger.info("   https://dashscope.aliyuncs.com/compatible-mode/v1")
        logger.info("2. 验证 API 密钥是否有效")
        logger.info("3. 检查网络连接")
    
    logger.info("? 测试完成")

if __name__ == "__main__":
    asyncio.run(main())