#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务失败回调使用示例
展示如何设置和使用自定义失败回调函数
"""
import asyncio
import logging
from typing import Dict, Any
from app.services.async_task_manager import task_manager, TaskType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def custom_failure_callback(failure_data: Dict[str, Any]):
    """自定义失败回调函数示例"""
    print(f"? 自定义回调：任务 {failure_data['task_id']} 失败了！")
    print(f"   错误信息: {failure_data['error_message']}")
    print(f"   重试次数: {failure_data['retry_count']}/{failure_data['max_retries']}")
    
    # 可以在这里添加自定义逻辑，如：
    # - 发送邮件通知
    # - 更新数据库状态  
    # - 触发补偿操作
    # - 记录到监控系统


def sync_failure_callback(failure_data: Dict[str, Any]):
    """同步失败回调函数示例"""
    print(f"? 同步回调：记录失败任务 {failure_data['task_id']}")
    # 同步操作，如写入文件、更新缓存等


async def main():
    """主函数 - 演示失败回调的使用"""
    
    print("=== 异步任务失败回调示例 ===\n")
    
    # 1. 添加全局失败回调（对所有任务生效）
    print("1. 添加全局失败回调...")
    task_manager.add_global_failure_callback(custom_failure_callback)
    task_manager.add_global_failure_callback(sync_failure_callback)
    
    # 2. 创建一个会失败的任务（使用无效的输入）
    print("2. 创建一个注定失败的任务...")
    
    # 创建任务时指定任务特定的失败回调
    async def task_specific_callback(failure_data: Dict[str, Any]):
        print(f"? 任务特定回调：处理任务 {failure_data['task_id']} 的失败")
    
    task_id = task_manager.create_task(
        task_type=TaskType.ZH2EN,
        input_data={"text": ""},  # 空文本会导致失败
        max_retries=2,  # 设置最大重试次数
        failure_callback=task_specific_callback  # 任务特定的失败回调
    )
    
    print(f"任务ID: {task_id}")
    
    # 3. 等待任务完成（失败）
    print("3. 等待任务执行...")
    await asyncio.sleep(5)  # 给任务一些时间执行
    
    # 4. 检查任务状态
    print("4. 检查任务状态...")
    status = task_manager.get_task_status(task_id)
    if status:
        print(f"任务状态: {status['status']}")
        if status['status'] == 'failed':
            print(f"错误信息: {status.get('error_message', 'N/A')}")
    
    # 5. 演示正常任务（不会失败）
    print("\n5. 创建一个正常任务作为对比...")
    normal_task_id = task_manager.create_task(
        task_type=TaskType.ZH2EN,
        input_data={"text": "你好世界"},
        max_retries=1,
    )
    
    await asyncio.sleep(3)
    normal_status = task_manager.get_task_status(normal_task_id)
    if normal_status:
        print(f"正常任务状态: {normal_status['status']}")
    
    # 6. 移除回调函数
    print("\n6. 移除自定义回调函数...")
    task_manager.remove_global_failure_callback(custom_failure_callback)
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())