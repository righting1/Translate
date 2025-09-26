#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
�����޸���� LangChain ������֤ 404 �����Ƿ���
"""
import logging
import sys
import os
import asyncio

# ������־
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_fixed_service():
    """�����޸���ķ���"""
    logger.info("=== �����޸���� LangChain ���� ===")
    
    try:
        # �������
        from services.langchain_service import LangChainManager
        from core.config import settings
        
        # �������
        logger.info("? �������:")
        logger.info(f"Ĭ��ģ��: {settings.ai_model.get('default_model')}")
        
        dashscope_config = settings.ai_model.get('dashscope', {})
        logger.info(f"DashScope ����:")
        logger.info(f"  - ��������: {dashscope_config.get('service_type')}")
        logger.info(f"  - ����URL: {dashscope_config.get('base_url')}")
        logger.info(f"  - ģ��: {dashscope_config.get('model')}")
        logger.info(f"  - API��Կ: {'***������***' if dashscope_config.get('api_key') else 'δ����'}")
        
        # ����������
        logger.info("? ���� LangChain ������...")
        manager = LangChainManager()
        
        # ��ȡ����
        logger.info("? ��ȡĬ�Ϸ���...")
        service = manager.get_default_service()
        
        if not service:
            logger.error("? �޷���ȡĬ�Ϸ���")
            return False
            
        if service.llm is None:
            logger.error("? service.llm Ϊ None")
            return False
            
        logger.info(f"? ���񴴽��ɹ�: {type(service.llm).__name__}")
        
        # ���Լ򵥵��ı�����
        logger.info("? ��ʼ�����ı�����...")
        test_prompt = "��˵ Hello"
        
        try:
            result = await service.generate_text(test_prompt)
            logger.info(f"? �ı����ɳɹ�!")
            logger.info(f"? ��Ӧ: {result}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"? �ı�����ʧ��: {error_msg}")
            
            if "404" in error_msg:
                logger.error("? ��Ȼ���� 404 ����")
                logger.info("����:")
                logger.info("1. API ��Կ�Ƿ���ȷ")
                logger.info("2. ���������Ƿ�����") 
                logger.info("3. DashScope �����Ƿ����")
            elif "401" in error_msg:
                logger.error("? ��֤ʧ�� - API ��Կ����")
            
            return False
            
    except Exception as e:
        logger.error(f"? ���Թ��̳����쳣: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

async def test_chain_execution():
    """������ִ��"""
    logger.info("=== ���� Chain ִ�� ===")
    
    try:
        from services.langchain_translate import LangChainTranslationService
        
        # �����������
        logger.info("? ���� LangChain �������...")
        translate_service = LangChainTranslationService(use_chains=False)  # �Ȳ�ʹ����
        
        # ���Լ򵥷���
        logger.info("? ������Ӣ�ķ���...")
        
        # �������ĵ�Ӣ��
        zh_text = "��ã�����"
        logger.info(f"�����ı�: {zh_text}")
        
        result = await translate_service.zh2en(zh_text)
        logger.info(f"? ��Ӣ����ɹ�: {result}")
        
        # ����Ӣ�ĵ�����
        en_text = "Hello, world"
        logger.info(f"�����ı�: {en_text}")
        
        result = await translate_service.en2zh(en_text)
        logger.info(f"? Ӣ�з���ɹ�: {result}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"? ��ִ�в���ʧ��: {error_msg}")
        
        if "404" in error_msg:
            logger.error("? ��ִ���з��� 404 ����")
            logger.info("����������ô�������")
        
        return False

async def main():
    """������"""
    logger.info("? ��ʼ 404 �����޸���֤...")
    
    # ���Ի�������
    basic_ok = await test_fixed_service()
    
    if basic_ok:
        logger.info("? �����������ͨ��")
        
        # ������ִ��
        chain_ok = await test_chain_execution()
        
        if chain_ok:
            logger.info("? ���в���ͨ����404 �������޸�")
        else:
            logger.warning("?? ��ִ�в���ʧ�ܣ���������������")
    else:
        logger.error("? �����������ʧ��")
        
        logger.info("? �޸�����:")
        logger.info("1. ��� config.yaml �е� base_url �Ƿ�Ϊ:")
        logger.info("   https://dashscope.aliyuncs.com/compatible-mode/v1")
        logger.info("2. ��֤ API ��Կ�Ƿ���Ч")
        logger.info("3. �����������")
    
    logger.info("? �������")

if __name__ == "__main__":
    asyncio.run(main())