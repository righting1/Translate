#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
���� LangChain �����ʼ������
"""
import logging
import sys
import os

# �����Ŀ·����Python·��
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ������ϸ��־
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

def debug_langchain_service():
    """���� LangChain �����ʼ��"""
    logger.info("=== ��ʼ���� LangChain ���� ===")
    
    try:
        # 1. �������
        from core.config import settings
        logger.info("���ü��سɹ�")
        
        if hasattr(settings, 'ai_model') and settings.ai_model:
            logger.info(f"AIģ�����ô��ڣ����� {len(settings.ai_model)} ��")
            
            for key, value in settings.ai_model.items():
                if key == 'default_model':
                    logger.info(f"Ĭ��ģ��: {value}")
                else:
                    logger.info(f"ģ������ '{key}': {type(value)} - enabled: {value.get('enabled', 'N/A') if isinstance(value, dict) else 'N/A'}")
                    
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if 'key' in sub_key.lower():  # API key ��������Ϣֻ��ʾ�Ƿ����
                                logger.info(f"  {sub_key}: {'[SET]' if sub_value else '[NOT SET]'}")
                            else:
                                logger.info(f"  {sub_key}: {sub_value}")
        else:
            logger.error("AIģ�����ò����ڻ�Ϊ��")
            return
            
        # 2. ��� LangChain ������
        try:
            from services.langchain_service import LANGCHAIN_AVAILABLE
            logger.info(f"LangChain ������: {LANGCHAIN_AVAILABLE}")
            
            if not LANGCHAIN_AVAILABLE:
                logger.error("LangChain �����ã����鰲װ")
                return
                
        except Exception as e:
            logger.error(f"���� LangChain ����ʧ��: {e}")
            return
            
        # 3. �������������������ʼ��
        from services.langchain_service import LangChainManager
        
        logger.info("���� LangChain ������...")
        manager = LangChainManager()
        
        logger.info(f"�����������ɹ�����������: {len(manager.services)}")
        
        for service_name, service in manager.services.items():
            logger.info(f"���� '{service_name}':")
            logger.info(f"  ����: {type(service).__name__}")
            logger.info(f"  ����: {service.config}")
            logger.info(f"  LLM: {type(service.llm).__name__ if service.llm else 'None'}")
            logger.info(f"  ��������: {service.service_type}")
            
        # 4. ���Ի�ȡ����
        logger.info("\n���Ի�ȡ����...")
        default_service = manager.get_service()
        
        if default_service:
            logger.info(f"��ȡ��Ĭ�Ϸ���: {type(default_service).__name__}")
            logger.info(f"Ĭ�Ϸ��� LLM: {type(default_service.llm).__name__ if default_service.llm else 'None'}")
            
            # 5. �����ı�����
            if default_service.llm is not None:
                logger.info("�����ı�����...")
                try:
                    import asyncio
                    result = asyncio.run(default_service.generate_text("Hello, this is a test."))
                    logger.info(f"�ı����ɽ��: {result}")
                except Exception as e:
                    logger.error(f"�ı�����ʧ��: {e}")
                    import traceback
                    logger.debug(f"��ϸ����: {traceback.format_exc()}")
            else:
                logger.error("Ĭ�Ϸ���� LLM Ϊ None���޷������ı�����")
                
        else:
            logger.error("��ȡĬ�Ϸ���ʧ��")
            
    except Exception as e:
        logger.error(f"���Թ����з�������: {e}")
        import traceback
        logger.error(f"��ϸ������Ϣ: {traceback.format_exc()}")
    
    logger.info("=== ������� ===")

if __name__ == "__main__":
    debug_langchain_service()