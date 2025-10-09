#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务管理系统
用于处理长时间运行的翻译和总结任务
"""
import asyncio
import uuid
import time
import logging
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待处理
    RUNNING = "running"      # 正在处理
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    EXPIRED = "expired"      # 已过期


class TaskType(str, Enum):
    """任务类型枚举"""
    ZH2EN = "zh2en"
    EN2ZH = "en2zh"
    SUMMARIZE = "summarize"
    KEYWORD_SUMMARY = "keyword_summary"
    STRUCTURED_SUMMARY = "structured_summary"


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    input_data: Dict[str, Any]
    result: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0  # 进度百分比 0-100
    model_name: Optional[str] = None
    use_chains: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 转换datetime为字符串
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 5, task_ttl_hours: int = 24):
        self.tasks: Dict[str, TaskInfo] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_ttl = timedelta(hours=task_ttl_hours)
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._cleanup_started = False
        
        # 启动清理任务（仅当存在运行中的事件循环时）
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._cleanup_expired_tasks())
            self._cleanup_started = True
        except RuntimeError:
            # 在无事件循环环境（如模块导入/测试收集时）跳过，待首次任务执行时再启动
            logger.debug("AsyncTaskManager: no running loop at init; will start cleanup later")
    
    def create_task(
        self,
        task_type: TaskType,
        input_data: Dict[str, Any],
        model_name: Optional[str] = None,
        use_chains: bool = True
    ) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            input_data=input_data,
            model_name=model_name,
            use_chains=use_chains
        )
        
        self.tasks[task_id] = task_info
        logger.info(f"Created task {task_id} of type {task_type}")
        
        # 异步执行任务
        try:
            task = asyncio.create_task(self._execute_task(task_id))
            self._running_tasks[task_id] = task
        except RuntimeError:
            # 无运行循环时，延迟到调用方事件循环中执行
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._execute_task(task_id))
            self._running_tasks[task_id] = task
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # 检查任务是否过期
        if self._is_task_expired(task):
            task.status = TaskStatus.EXPIRED
            task.updated_at = datetime.now()
        
        return task.to_dict()
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        if task.status == TaskStatus.COMPLETED:
            return {
                "task_id": task_id,
                "status": task.status,
                "result": task.result,
                "model_name": task.model_name,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
        elif task.status == TaskStatus.FAILED:
            return {
                "task_id": task_id,
                "status": task.status,
                "error": task.error_message,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
        else:
            return {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            # 取消正在运行的任务
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()
                del self._running_tasks[task_id]
            
            task.status = TaskStatus.FAILED
            task.error_message = "Task cancelled by user"
            task.updated_at = datetime.now()
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """列出所有任务"""
        tasks = []
        for task in self.tasks.values():
            if status is None or task.status == status:
                tasks.append(task.to_dict())
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x['created_at'], reverse=True)
        return tasks
    
    async def _execute_task(self, task_id: str):
        """执行任务"""
        # 确保清理任务已启动
        if not self._cleanup_started:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._cleanup_expired_tasks())
                self._cleanup_started = True
            except RuntimeError:
                pass
        async with self._semaphore:  # 限制并发数
            task = self.tasks.get(task_id)
            if not task:
                return
            
            try:
                # 更新任务状态为运行中
                task.status = TaskStatus.RUNNING
                task.updated_at = datetime.now()
                task.progress = 10
                logger.info(f"Starting execution of task {task_id}")
                
                # 导入服务
                from .langchain_translate import LangChainTranslationService
                service = LangChainTranslationService(
                    model_name=task.model_name,
                    use_chains=task.use_chains
                )
                
                # 更新进度
                task.progress = 30
                task.updated_at = datetime.now()
                
                # 根据任务类型执行相应的操作
                if task.task_type == TaskType.ZH2EN:
                    result = await service.zh2en(task.input_data['text'])
                elif task.task_type == TaskType.EN2ZH:
                    result = await service.en2zh(task.input_data['text'])
                elif task.task_type == TaskType.SUMMARIZE:
                    max_length = task.input_data.get('max_length', 200)
                    result = await service.summarize(task.input_data['text'], max_length=max_length)
                elif task.task_type == TaskType.KEYWORD_SUMMARY:
                    summary_length = task.input_data.get('summary_length', 100)
                    result = await service.keyword_summary(task.input_data['text'], summary_length=summary_length)
                elif task.task_type == TaskType.STRUCTURED_SUMMARY:
                    max_length = task.input_data.get('max_length', 300)
                    result = await service.structured_summary(task.input_data['text'], max_length=max_length)
                else:
                    raise ValueError(f"Unsupported task type: {task.task_type}")
                
                # 任务完成
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.updated_at = datetime.now()
                logger.info(f"Task {task_id} completed successfully")
                
            except asyncio.CancelledError:
                task.status = TaskStatus.FAILED
                task.error_message = "Task was cancelled"
                task.updated_at = datetime.now()
                logger.info(f"Task {task_id} was cancelled")
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.updated_at = datetime.now()
                logger.error(f"Task {task_id} failed: {e}")
            finally:
                # 清理运行中的任务记录
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]
    
    def _is_task_expired(self, task: TaskInfo) -> bool:
        """检查任务是否过期"""
        return datetime.now() - task.created_at > self.task_ttl
    
    async def _cleanup_expired_tasks(self):
        """定期清理过期任务"""
        while True:
            try:
                expired_tasks = []
                for task_id, task in self.tasks.items():
                    if self._is_task_expired(task):
                        expired_tasks.append(task_id)
                
                for task_id in expired_tasks:
                    del self.tasks[task_id]
                    logger.info(f"Cleaned up expired task {task_id}")
                
                # 每小时清理一次
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)  # 出错后5分钟后重试


# 全局任务管理器实例
task_manager = AsyncTaskManager()