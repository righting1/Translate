#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回调函数注册和管理系统
支持基于配置动态选择和创建回调函数
"""
import logging
from typing import Dict, Any, Callable, Optional
from .failure_callbacks import (
    log_failure_callback,
    save_failure_to_file_callback,
    send_notification_callback,
    cleanup_failed_task_data_callback
)

logger = logging.getLogger(__name__)


class CallbackRegistry:
    """回调函数注册中心"""
    
    def __init__(self):
        self._callbacks: Dict[str, Callable] = {}
        self._register_default_callbacks()
    
    def _register_default_callbacks(self):
        """注册默认的回调函数"""
        self.register("log_failure", log_failure_callback)
        self.register("save_failure_details", save_failure_to_file_callback)
        self.register("send_notification", send_notification_callback)
        self.register("cleanup_task_data", cleanup_failed_task_data_callback)
    
    def register(self, name: str, callback: Callable):
        """注册回调函数"""
        self._callbacks[name] = callback
        logger.info(f"Registered callback: {name}")
    
    def get(self, name: str) -> Optional[Callable]:
        """获取回调函数"""
        return self._callbacks.get(name)
    
    def list_available(self) -> list:
        """列出所有可用的回调函数"""
        return list(self._callbacks.keys())
    
    def create_configured_callback(self, config: Dict[str, Any]) -> Optional[Callable]:
        """根据配置创建回调函数"""
        if not config:
            return None
        
        async def configured_callback(failure_data: Dict[str, Any]):
            """配置化的回调函数"""
            try:
                # 执行基础日志记录
                await log_failure_callback(failure_data)
                
                # 根据配置执行其他回调
                if config.get("save_failure_details", True):
                    await save_failure_to_file_callback(failure_data)
                
                if config.get("enable_notifications", False):
                    await send_notification_callback(failure_data)
                
                if config.get("cleanup_task_data", True):
                    await cleanup_failed_task_data_callback(failure_data)
                
                # 执行自定义回调
                custom_callback_name = config.get("custom_callback_name")
                if custom_callback_name:
                    custom_callback = self.get(custom_callback_name)
                    if custom_callback:
                        await custom_callback(failure_data)
                    else:
                        logger.warning(f"Custom callback '{custom_callback_name}' not found")
                
            except Exception as e:
                logger.error(f"Error in configured callback: {e}")
        
        return configured_callback


# 全局回调注册中心
callback_registry = CallbackRegistry()


def create_email_notification_callback(email: str) -> Callable:
    """创建邮件通知回调函数"""
    async def email_notification_callback(failure_data: Dict[str, Any]):
        try:
            # 这里可以集成真实的邮件服务
            # 示例：使用 smtplib 发送邮件
            message = f"""
            异步任务失败通知
            
            任务ID: {failure_data['task_id']}
            任务类型: {failure_data['task_type']}
            错误信息: {failure_data['error_message']}
            重试次数: {failure_data['retry_count']}/{failure_data['max_retries']}
            失败时间: {failure_data['failed_at']}
            
            请检查系统状态并处理相关问题。
            """
            
            # 这里应该是真实的邮件发送逻辑
            logger.info(f"Would send email notification to {email}: {message[:100]}...")
            
            # 临时保存到文件作为示例
            import os
            from pathlib import Path
            
            notification_dir = Path("logs/email_notifications")
            notification_dir.mkdir(parents=True, exist_ok=True)
            
            with open(notification_dir / f"email_{failure_data['task_id']}.txt", 'w', encoding='utf-8') as f:
                f.write(f"To: {email}\n")
                f.write(f"Subject: 任务失败通知 - {failure_data['task_id']}\n\n")
                f.write(message)
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    return email_notification_callback


def create_webhook_callback(webhook_url: str) -> Callable:
    """创建 Webhook 回调函数"""
    async def webhook_callback(failure_data: Dict[str, Any]):
        try:
            import httpx
            
            payload = {
                "event": "task_failed",
                "task_id": failure_data['task_id'],
                "task_type": failure_data['task_type'],
                "error_message": failure_data['error_message'],
                "retry_count": failure_data['retry_count'],
                "max_retries": failure_data['max_retries'],
                "failed_at": failure_data['failed_at'].isoformat() if hasattr(failure_data['failed_at'], 'isoformat') else str(failure_data['failed_at'])
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
                
            logger.info(f"Sent webhook notification to {webhook_url}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    return webhook_callback


# 注册额外的回调函数示例
def register_custom_callbacks():
    """注册自定义回调函数"""
    
    async def slack_notification_callback(failure_data: Dict[str, Any]):
        """Slack 通知回调（示例）"""
        # 这里可以集成 Slack API
        logger.info(f"Would send Slack notification for task {failure_data['task_id']}")
    
    async def database_log_callback(failure_data: Dict[str, Any]):
        """数据库日志回调（示例）"""
        # 这里可以将失败信息记录到数据库
        logger.info(f"Would log task {failure_data['task_id']} failure to database")
    
    callback_registry.register("slack_notification", slack_notification_callback)
    callback_registry.register("database_log", database_log_callback)