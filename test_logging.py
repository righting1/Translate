#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志系统是否正常工作
"""
import logging
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 确保输出到标准输出
    ]
)

# 测试基本日志
logger = logging.getLogger(__name__)
logger.info("=== 日志测试开始 ===")

# 测试不同级别的日志
logger.debug("这是DEBUG级别日志")
logger.info("这是INFO级别日志")
logger.warning("这是WARNING级别日志")
logger.error("这是ERROR级别日志")

# 测试导入和配置
try:
    from core.config import settings
    logger.info("配置文件导入成功")
    logger.info(f"应用名称: {settings.app_name}")
    logger.info(f"日志级别配置: {settings.log_level}")
    
    if hasattr(settings, 'ai_model') and settings.ai_model:
        logger.info(f"AI模型配置存在: {len(settings.ai_model)} 项")
        logger.info(f"默认模型: {settings.ai_model.get('default_model', 'None')}")
        
        for key in settings.ai_model.keys():
            if key != 'default_model':
                logger.debug(f"模型配置 {key}: {type(settings.ai_model[key])}")
    else:
        logger.warning("AI模型配置不存在或为空")
        
except Exception as e:
    logger.error(f"导入配置失败: {e}")

# 测试LangChain服务
try:
    from services.langchain_service import LangChainManager
    logger.info("LangChain服务模块导入成功")
    
    # 创建管理器实例
    manager = LangChainManager()
    logger.info("LangChain管理器创建成功")
    
    # 测试获取服务
    service = manager.get_service()
    logger.info(f"获取服务结果: {service is not None}")
    
except Exception as e:
    logger.error(f"LangChain服务测试失败: {e}")
    import traceback
    logger.error(f"详细错误信息: {traceback.format_exc()}")

logger.info("=== 日志测试完成 ===")