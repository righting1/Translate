#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
������־ϵͳ�Ƿ���������
"""
import logging
import sys
import os

# �����Ŀ·����Python·��
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ������־
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # ȷ���������׼���
    ]
)

# ���Ի�����־
logger = logging.getLogger(__name__)
logger.info("=== ��־���Կ�ʼ ===")

# ���Բ�ͬ�������־
logger.debug("����DEBUG������־")
logger.info("����INFO������־")
logger.warning("����WARNING������־")
logger.error("����ERROR������־")

# ���Ե��������
try:
    from core.config import settings
    logger.info("�����ļ�����ɹ�")
    logger.info(f"Ӧ������: {settings.app_name}")
    logger.info(f"��־��������: {settings.log_level}")
    
    if hasattr(settings, 'ai_model') and settings.ai_model:
        logger.info(f"AIģ�����ô���: {len(settings.ai_model)} ��")
        logger.info(f"Ĭ��ģ��: {settings.ai_model.get('default_model', 'None')}")
        
        for key in settings.ai_model.keys():
            if key != 'default_model':
                logger.debug(f"ģ������ {key}: {type(settings.ai_model[key])}")
    else:
        logger.warning("AIģ�����ò����ڻ�Ϊ��")
        
except Exception as e:
    logger.error(f"��������ʧ��: {e}")

# ����LangChain����
try:
    from services.langchain_service import LangChainManager
    logger.info("LangChain����ģ�鵼��ɹ�")
    
    # ����������ʵ��
    manager = LangChainManager()
    logger.info("LangChain�����������ɹ�")
    
    # ���Ի�ȡ����
    service = manager.get_service()
    logger.info(f"��ȡ������: {service is not None}")
    
except Exception as e:
    logger.error(f"LangChain�������ʧ��: {e}")
    import traceback
    logger.error(f"��ϸ������Ϣ: {traceback.format_exc()}")

logger.info("=== ��־������� ===")