#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务失败回调函数集合
提供各种常用的失败处理回调函数
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


async def log_failure_callback(failure_data: Dict[str, Any]):
    """记录失败信息到日志的回调函数"""
    logger.error(
        f"Task {failure_data['task_id']} ({failure_data['task_type']}) failed: "
        f"{failure_data['error_message']} "
        f"(Retry {failure_data['retry_count']}/{failure_data['max_retries']})"
    )


async def save_failure_to_file_callback(failure_data: Dict[str, Any]):
    """将失败信息保存到文件的回调函数"""
    try:
        # 创建失败日志目录
        failure_log_dir = Path("logs/failures")
        failure_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_failure_{failure_data['task_id']}_{timestamp}.json"
        filepath = failure_log_dir / filename
        
        # 准备保存的数据
        save_data = {
            **failure_data,
            "created_at": failure_data['created_at'].isoformat() if hasattr(failure_data['created_at'], 'isoformat') else str(failure_data['created_at']),
            "failed_at": failure_data['failed_at'].isoformat() if hasattr(failure_data['failed_at'], 'isoformat') else str(failure_data['failed_at'])
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved failure details to {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to save failure details to file: {e}")


async def send_notification_callback(failure_data: Dict[str, Any]):
    """发送通知的回调函数（示例）"""
    try:
        # 这里可以集成各种通知服务，如邮件、Slack、钉钉等
        notification_message = (
            f"🚨 异步任务失败通知\n"
            f"任务ID: {failure_data['task_id']}\n"
            f"任务类型: {failure_data['task_type']}\n"
            f"错误信息: {failure_data['error_message']}\n"
            f"重试次数: {failure_data['retry_count']}/{failure_data['max_retries']}\n"
            f"失败时间: {failure_data['failed_at']}"
        )
        
        # 示例：保存通知到文件（实际使用时可以替换为真实的通知服务）
        notification_file = Path("logs/notifications.txt")
        notification_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(notification_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {notification_message}\n\n")
        
        logger.info(f"Sent failure notification for task {failure_data['task_id']}")
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


async def retry_with_different_model_callback(failure_data: Dict[str, Any]):
    """使用不同模型重试的回调函数"""
    try:
        # 这是一个示例回调，展示如何在失败时尝试使用不同的模型
        from .async_task_manager import task_manager, TaskType
        
        # 如果还有重试机会且错误与模型相关
        if (failure_data['retry_count'] < failure_data['max_retries'] and 
            any(keyword in failure_data['error_message'].lower() for keyword in 
                ['model', 'api', 'token', 'rate limit'])):
            
            # 模型备选列表
            model_alternatives = ['openai', 'dashscope', 'zhipuai']
            current_model = failure_data.get('model_name', 'openai')
            
            # 选择不同的模型
            next_model = None
            for model in model_alternatives:
                if model != current_model:
                    next_model = model
                    break
            
            if next_model:
                logger.info(f"Attempting to retry task {failure_data['task_id']} with model {next_model}")
                
                # 创建新任务使用不同的模型（这里只是示例，实际实现需要更仔细的设计）
                # task_manager.create_task(
                #     task_type=TaskType(failure_data['task_type']),
                #     input_data=failure_data['input_data'],
                #     model_name=next_model,
                #     max_retries=1  # 限制重试次数避免无限递归
                # )
        
    except Exception as e:
        logger.error(f"Failed to retry with different model: {e}")


async def cleanup_failed_task_data_callback(failure_data: Dict[str, Any]):
    """清理失败任务数据的回调函数"""
    try:
        # 如果任务彻底失败（已达到最大重试次数），可以进行一些清理工作
        if failure_data['retry_count'] >= failure_data['max_retries']:
            # 清理临时文件
            temp_dir = Path(f"temp/task_{failure_data['task_id']}")
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary files for failed task {failure_data['task_id']}")
            
            # 记录失败统计
            stats_file = Path("logs/failure_stats.json")
            stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            stats = {}
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            
            task_type = failure_data['task_type']
            if task_type not in stats:
                stats[task_type] = {"total_failures": 0, "last_failure": None}
            
            stats[task_type]["total_failures"] += 1
            stats[task_type]["last_failure"] = failure_data['failed_at'].isoformat() if hasattr(failure_data['failed_at'], 'isoformat') else str(failure_data['failed_at'])
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
    except Exception as e:
        logger.error(f"Failed to cleanup task data: {e}")


# 预定义的回调函数列表
DEFAULT_FAILURE_CALLBACKS = [
    log_failure_callback,
    save_failure_to_file_callback,
    # send_notification_callback,  # 可选启用
    # retry_with_different_model_callback,  # 可选启用
    cleanup_failed_task_data_callback,
]


def register_default_callbacks(task_manager):
    """注册默认的失败回调函数"""
    for callback in DEFAULT_FAILURE_CALLBACKS:
        task_manager.add_global_failure_callback(callback)
    logger.info(f"Registered {len(DEFAULT_FAILURE_CALLBACKS)} default failure callbacks")