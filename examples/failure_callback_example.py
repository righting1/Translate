#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
�첽����ʧ�ܻص�ʹ��ʾ��
չʾ������ú�ʹ���Զ���ʧ�ܻص�����
"""
import asyncio
import logging
from typing import Dict, Any
from app.services.async_task_manager import task_manager, TaskType

# ������־
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def custom_failure_callback(failure_data: Dict[str, Any]):
    """�Զ���ʧ�ܻص�����ʾ��"""
    print(f"? �Զ���ص������� {failure_data['task_id']} ʧ���ˣ�")
    print(f"   ������Ϣ: {failure_data['error_message']}")
    print(f"   ���Դ���: {failure_data['retry_count']}/{failure_data['max_retries']}")
    
    # ��������������Զ����߼����磺
    # - �����ʼ�֪ͨ
    # - �������ݿ�״̬  
    # - ������������
    # - ��¼�����ϵͳ


def sync_failure_callback(failure_data: Dict[str, Any]):
    """ͬ��ʧ�ܻص�����ʾ��"""
    print(f"? ͬ���ص�����¼ʧ������ {failure_data['task_id']}")
    # ͬ����������д���ļ������»����


async def main():
    """������ - ��ʾʧ�ܻص���ʹ��"""
    
    print("=== �첽����ʧ�ܻص�ʾ�� ===\n")
    
    # 1. ���ȫ��ʧ�ܻص���������������Ч��
    print("1. ���ȫ��ʧ�ܻص�...")
    task_manager.add_global_failure_callback(custom_failure_callback)
    task_manager.add_global_failure_callback(sync_failure_callback)
    
    # 2. ����һ����ʧ�ܵ�����ʹ����Ч�����룩
    print("2. ����һ��ע��ʧ�ܵ�����...")
    
    # ��������ʱָ�������ض���ʧ�ܻص�
    async def task_specific_callback(failure_data: Dict[str, Any]):
        print(f"? �����ض��ص����������� {failure_data['task_id']} ��ʧ��")
    
    task_id = task_manager.create_task(
        task_type=TaskType.ZH2EN,
        input_data={"text": ""},  # ���ı��ᵼ��ʧ��
        max_retries=2,  # ����������Դ���
        failure_callback=task_specific_callback  # �����ض���ʧ�ܻص�
    )
    
    print(f"����ID: {task_id}")
    
    # 3. �ȴ�������ɣ�ʧ�ܣ�
    print("3. �ȴ�����ִ��...")
    await asyncio.sleep(5)  # ������һЩʱ��ִ��
    
    # 4. �������״̬
    print("4. �������״̬...")
    status = task_manager.get_task_status(task_id)
    if status:
        print(f"����״̬: {status['status']}")
        if status['status'] == 'failed':
            print(f"������Ϣ: {status.get('error_message', 'N/A')}")
    
    # 5. ��ʾ�������񣨲���ʧ�ܣ�
    print("\n5. ����һ������������Ϊ�Ա�...")
    normal_task_id = task_manager.create_task(
        task_type=TaskType.ZH2EN,
        input_data={"text": "�������"},
        max_retries=1,
    )
    
    await asyncio.sleep(3)
    normal_status = task_manager.get_task_status(normal_task_id)
    if normal_status:
        print(f"��������״̬: {normal_status['status']}")
    
    # 6. �Ƴ��ص�����
    print("\n6. �Ƴ��Զ���ص�����...")
    task_manager.remove_global_failure_callback(custom_failure_callback)
    
    print("\n=== ʾ����� ===")


if __name__ == "__main__":
    asyncio.run(main())