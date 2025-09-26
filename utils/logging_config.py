#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置和管理
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
    设置项目日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果不设置则只输出到控制台
        format_string: 自定义日志格式
    """
    # 默认日志格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建日志配置字典
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
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
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
        
        # 将文件处理器添加到根记录器
        config['loggers']['']['handlers'].append('file')
    
    # 应用日志配置
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 记录器名称，通常使用 __name__
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)

# 项目日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO, 
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 示例使用方法
if __name__ == "__main__":
    # 设置日志配置
    setup_logging(
        level="DEBUG",
        log_file="logs/app.log"
    )
    
    # 获取日志记录器
    logger = get_logger(__name__)
    
    # 使用示例
    logger.debug("这是一个调试信息")
    logger.info("这是一个信息")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")
    logger.critical("这是一个严重错误")