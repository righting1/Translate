#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain 404������Ϻ��޸��ű�
"""
import logging
import sys
import os
import asyncio

# �����Ŀ·��
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ������־
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_langchain_service():
    """���� LangChain ������� 404 ����"""
    logger.info("=== ��ʼ LangChain ������� ===")
    
    try:
        # 1. ��������
        from core.config import settings
        logger.info("? �����ļ�����ɹ�")
        
        # 2. �������
        if hasattr(settings, 'ai_model') and settings.ai_model:
            logger.info(f"? AIģ�����ô���: {list(settings.ai_model.keys())}")
            default_model = settings.ai_model.get('default_model', 'None')
            logger.info(f"Ĭ��ģ��: {default_model}")
            
            # ����������
            if default_model in settings.ai_model:
                config = settings.ai_model[default_model]
                logger.info(f"Ĭ��ģ������:")
                logger.info(f"  - ��������: {config.get('service_type')}")
                logger.info(f"  - ģ������: {config.get('model')}")
                logger.info(f"  - ����URL: {config.get('base_url')}")
                logger.info(f"  - API��Կ: {'***������***' if config.get('api_key') else 'δ����'}")
        else:
            logger.error("? AIģ�����ò�����")
            return False
        
        # 3. ��������
        from services.langchain_service import LangChainManager
        manager = LangChainManager()
        logger.info("? LangChain�����������ɹ�")
        
        # 4. ��ȡĬ�Ϸ���
        service = manager.get_default_service()
        if service:
            logger.info("? ��ȡĬ�Ϸ���ɹ�")
            logger.info(f"������Ϣ:")
            logger.info(f"  - ����: {type(service).__name__}")
            logger.info(f"  - ģ����: {service.model_name}")
            logger.info(f"  - ��������: {service.service_type}")
            logger.info(f"  - LLM����: {type(service.llm).__name__ if service.llm else 'None'}")
            
            # 5. ��� LLM ��ʼ��
            if service.llm is None:
                logger.error("? self.llm Ϊ None���������³�ʼ��...")
                service._initialize_llm()
                if service.llm:
                    logger.info("? ���³�ʼ���ɹ�")
                else:
                    logger.error("? ���³�ʼ��ʧ��")
                    return False
            
            # 6. �����ı�����
            logger.info("��ʼ�����ı�����...")
            test_prompt = "Say hello"
            
            try:
                result = await service.generate_text(test_prompt)
                logger.info(f"? �ı����ɳɹ�: {result[:100]}...")
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"? �ı�����ʧ��: {error_msg}")
                
                # 404 �������
                if "404" in error_msg:
                    logger.error("? ���� 404 ����!")
                    logger.error("���ܵ�ԭ��:")
                    logger.error("1. API�˵�URL����ȷ")
                    logger.error("2. ģ�����Ʋ�����")
                    logger.error("3. ���񲻿���")
                    
                    # �޸�����
                    logger.info("? �޸�����:")
                    if service.service_type == "dashscope":
                        logger.info("DashScope ��ȷ����:")
                        logger.info("  base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1'")
                        logger.info("  model: 'qwen-turbo' �� 'qwen-plus'")
                    elif service.service_type == "openai":
                        logger.info("OpenAI ��ȷ����:")
                        logger.info("  base_url: �����ã�ʹ��Ĭ�ϣ�����ȷ�Ĵ���URL")
                        logger.info("  model: 'gpt-3.5-turbo' ��������Чģ��")
                        
                return False
                
        else:
            logger.error("? ��ȡĬ�Ϸ���ʧ��")
            return False
            
    except Exception as e:
        logger.error(f"? ���Թ����г����쳣: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def provide_fix_recommendations():
    """�ṩ�޸�����"""
    logger.info("=== �޸����� ===")
    
    logger.info("1. ��� config.yaml ����:")
    logger.info("""
ai_model:
  default_model: "dashscope"  # �� "openai"
  dashscope:
    service_type: "dashscope"
    model: "qwen-turbo"
    api_key: "your_dashscope_api_key"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    temperature: 0.7
    max_tokens: 2000
""")
    
    logger.info("2. ���û�������:")
    logger.info("   PowerShell: $env:DASHSCOPE_API_KEY='your_api_key'")
    logger.info("   CMD: set DASHSCOPE_API_KEY=your_api_key")
    
    logger.info("3. ���� 404 ������:")
    logger.info("   - ȷ�� base_url ��ȷ")
    logger.info("   - ���ģ�������Ƿ���Ч")
    logger.info("   - ��֤ API ����״̬")

async def main():
    """������"""
    logger.info("��ʼ LangChain 404 �������...")
    
    success = await test_langchain_service()
    
    if not success:
        provide_fix_recommendations()
    
    logger.info("=== ������ ===")

if __name__ == "__main__":
    asyncio.run(main())