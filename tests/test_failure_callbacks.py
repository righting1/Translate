#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务失败回调功能测试脚本
"""
import asyncio
import requests
import json
import time
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_create_task_with_failure_callback():
    """测试创建带有失败回调配置的任务"""
    print("=== 测试带失败回调的异步任务 ===\n")
    
    # 1. 测试列出可用回调
    print("1. 获取可用的回调函数...")
    response = requests.get(f"{BASE_URL}/api/translate/async/callbacks/available")
    if response.status_code == 200:
        callbacks_info = response.json()
        print(f"✓ 可用回调函数: {callbacks_info['available_callbacks']}")
        print(f"✓ 回调描述: {json.dumps(callbacks_info['description'], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 获取回调信息失败: {response.status_code}")
        return
    
    print()
    
    # 2. 测试回调函数
    print("2. 测试回调函数...")
    test_callback = "log_failure"
    response = requests.post(
        f"{BASE_URL}/api/translate/async/callbacks/test",
        params={"callback_name": test_callback}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 回调函数 '{test_callback}' 测试成功: {result['message']}")
    else:
        print(f"❌ 回调函数测试失败: {response.status_code}")
    
    print()
    
    # 3. 创建会失败的任务
    print("3. 创建会失败的任务...")
    task_config = {
        "text": "xxx",  #
        "model": "openaixx",# 使用错误的模型
        "config": {
            "max_retries": 2,
            "enable_notifications": True,
            "save_failure_details": True,
            "notification_email": "test@example.com",
            "custom_callback_name": "log_failure"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/translate/async/zh2en",
        json=task_config,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"✓ 任务创建成功: {task_id}")
        
        # 4. 监控任务状态
        print("4. 监控任务状态...")
        for i in range(10):  # 最多等待10次
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/translate/async/status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   第{i+1}次检查 - 状态: {status_data['status']}")
                
                if status_data['status'] == 'failed':
                    print(f"✓ 任务失败（符合预期）: {status_data.get('error_message', 'N/A')}")
                    break
                elif status_data['status'] == 'completed':
                    print("❌ 任务意外完成了")
                    break
            else:
                print(f"❌ 获取状态失败: {status_response.status_code}")
                break
        
        # 5. 检查失败日志文件
        print("5. 检查失败回调效果...")
        import os
        from pathlib import Path
        
        # 检查是否生成了失败日志文件
        failure_log_dir = Path("logs/failures")
        if failure_log_dir.exists():
            failure_files = list(failure_log_dir.glob(f"task_failure_{task_id}_*.json"))
            if failure_files:
                print(f"✓ 生成了失败详情文件: {failure_files[0].name}")
                
                # 读取失败详情
                with open(failure_files[0], 'r', encoding='utf-8') as f:
                    failure_data = json.load(f)
                    print(f"   错误信息: {failure_data.get('error_message', 'N/A')}")
                    print(f"   重试次数: {failure_data.get('retry_count', 0)}")
            else:
                print("❌ 未找到失败详情文件")
        else:
            print("❌ 失败日志目录不存在")
        
        # 检查邮件通知文件
        email_notification_dir = Path("logs/email_notifications")
        if email_notification_dir.exists():
            email_files = list(email_notification_dir.glob(f"email_{task_id}.txt"))
            if email_files:
                print(f"✓ 生成了邮件通知文件: {email_files[0].name}")
            else:
                print("❌ 未找到邮件通知文件")
        else:
            print("❌ 邮件通知目录不存在")
            
    else:
        print(f"❌ 任务创建失败: {response.status_code}")
        print(f"错误内容: {response.text}")
    
    print()


def test_normal_task_with_callback():
    """测试正常任务的回调配置（不应触发失败回调）"""
    print("=== 测试正常任务（不触发失败回调） ===\n")
    
    task_config = {
        "text": "你好，世界！",  # 正常文本
        "model": "dashscope",
        "config": {
            "max_retries": 1,
            "enable_notifications": True,
            "save_failure_details": True,
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/translate/async/zh2en",
        json=task_config,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"✓ 正常任务创建成功: {task_id}")
        
        # 等待任务完成
        for i in range(5):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/translate/async/status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   第{i+1}次检查 - 状态: {status_data['status']}")
                
                if status_data['status'] == 'completed':
                    print("✓ 正常任务完成（未触发失败回调）")
                    break
                elif status_data['status'] == 'failed':
                    print("❌ 正常任务意外失败")
                    break
        
    else:
        print(f"❌ 正常任务创建失败: {response.status_code}")
    
    print()


def main():
    """主测试函数"""
    print("异步任务失败回调功能测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ 服务健康检查失败: {response.status_code}")
            return
        print("✓ 服务运行正常\n")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请确保服务正在运行在 http://localhost:8000")
        return
    
    # 运行测试
    try:
        test_create_task_with_failure_callback()
        test_normal_task_with_callback()
        
        print("=== 测试完成 ===")
        print("请检查 logs/ 目录下的文件以确认回调函数正常工作")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()