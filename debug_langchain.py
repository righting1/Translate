#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 LangChain 服务初始化问题
"""
import logging
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

def debug_langchain_service():
    """调试 LangChain 服务初始化"""
    logger.info("=== 开始调试 LangChain 服务 ===")
    
    try:
        # 1. 检查配置
        from core.config import settings
        logger.info("配置加载成功")
        
        if hasattr(settings, 'ai_model') and settings.ai_model:
            logger.info(f"AI模型配置存在，包含 {len(settings.ai_model)} 项")
            
            for key, value in settings.ai_model.items():
                if key == 'default_model':
                    logger.info(f"默认模型: {value}")
                else:
                    logger.info(f"模型配置 '{key}': {type(value)} - enabled: {value.get('enabled', 'N/A') if isinstance(value, dict) else 'N/A'}")
                    
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if 'key' in sub_key.lower():  # API key 等敏感信息只显示是否存在
                                logger.info(f"  {sub_key}: {'[SET]' if sub_value else '[NOT SET]'}")
                            else:
                                logger.info(f"  {sub_key}: {sub_value}")
        else:
            logger.error("AI模型配置不存在或为空")
            return
            
        # 2. 检查 LangChain 可用性
        try:
            from services.langchain_service import LANGCHAIN_AVAILABLE
            logger.info(f"LangChain 可用性: {LANGCHAIN_AVAILABLE}")
            
            if not LANGCHAIN_AVAILABLE:
                logger.error("LangChain 不可用，请检查安装")
                return
                
        except Exception as e:
            logger.error(f"导入 LangChain 服务失败: {e}")
            return
            
        # 3. 创建管理器并检查服务初始化
        from services.langchain_service import LangChainManager
        
        logger.info("创建 LangChain 管理器...")
        manager = LangChainManager()
        
        logger.info(f"管理器创建成功，服务数量: {len(manager.services)}")
        
        for service_name, service in manager.services.items():
            logger.info(f"服务 '{service_name}':")
            logger.info(f"  类型: {type(service).__name__}")
            logger.info(f"  配置: {service.config}")
            logger.info(f"  LLM: {type(service.llm).__name__ if service.llm else 'None'}")
            logger.info(f"  服务类型: {service.service_type}")
            
        # 4. 测试获取服务
        logger.info("\n测试获取服务...")
        default_service = manager.get_service()
        
        if default_service:
            logger.info(f"获取到默认服务: {type(default_service).__name__}")
            logger.info(f"默认服务 LLM: {type(default_service.llm).__name__ if default_service.llm else 'None'}")
            
            # 5. 测试文本生成
            if default_service.llm is not None:
                logger.info("测试文本生成...")
                try:
                    import asyncio
                    result = asyncio.run(default_service.generate_text("Hello, this is a test."))
                    logger.info(f"文本生成结果: {result}")
                except Exception as e:
                    logger.error(f"文本生成失败: {e}")
                    import traceback
                    logger.debug(f"详细错误: {traceback.format_exc()}")
            else:
                logger.error("默认服务的 LLM 为 None，无法测试文本生成")
                
        else:
            logger.error("获取默认服务失败")
            
    except Exception as e:
        logger.error(f"调试过程中发生错误: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    logger.info("=== 调试完成 ===")

if __name__ == "__main__":
    debug_langchain_service()