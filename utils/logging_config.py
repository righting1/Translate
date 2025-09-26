#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
��־����ģ��
�ṩͳһ����־���ú͹���
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    ������Ŀ��־����
    
    Args:
        level: ��־���� (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ��־�ļ�·���������������ֻ���������̨
        format_string: �Զ�����־��ʽ
    """
    # Ĭ����־��ʽ
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ������־�����ֵ�
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': format_string,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level.upper(),
                'formatter': 'standard',
                'stream': sys.stdout
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': level.upper(),
                'propagate': False
            }
        }
    }
    
    # ���ָ������־�ļ�������ļ�������
    if log_file:
        # ȷ����־Ŀ¼����
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level.upper(),
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        
        # ���ļ���������ӵ�����¼��
        config['loggers']['']['handlers'].append('file')
    
    # Ӧ����־����
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """
    ��ȡ��־��¼��
    
    Args:
        name: ��¼�����ƣ�ͨ��ʹ�� __name__
        
    Returns:
        ���úõ���־��¼��
    """
    return logging.getLogger(name)

# ��Ŀ��־����ӳ��
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO, 
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# ʾ��ʹ�÷���
if __name__ == "__main__":
    # ������־����
    setup_logging(
        level="DEBUG",
        log_file="logs/app.log"
    )
    
    # ��ȡ��־��¼��
    logger = get_logger(__name__)
    
    # ʹ��ʾ��
    logger.debug("����һ��������Ϣ")
    logger.info("����һ����Ϣ")
    logger.warning("����һ������")
    logger.error("����һ������")
    logger.critical("����һ�����ش���")