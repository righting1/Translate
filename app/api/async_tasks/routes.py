from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import logging
import httpx

from ...schemas.translate import SimpleTextRequest, AsyncTaskRequest
from ...services.async_task_manager import task_manager, TaskType, TaskStatus
from ...services.callback_registry import callback_registry, create_email_notification_callback
from ...utils.exceptions import (
    EmptyTextError,
    TextTooLongError,
    TaskNotFoundException,
    TaskAlreadyCompletedError,
    ModelAPIError,
    TranslateAPIException
)


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/translate/async", tags=["async-tasks"])


@router.post("/zh2en")
async def submit_async_zh2en_task(
    req: AsyncTaskRequest,
):
    """
    提交异步中译英任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    # 验证输入
    if not req.text or not req.text.strip():
        raise EmptyTextError()

    # 兼容空字符串模型名，统一使用默认模型
    model_name = (getattr(req, 'model', None) or "").strip() or None
    logger.info(f"提交异步中译英任务: text_length={len(req.text)}, model={model_name}")

    # 创建配置化的失败回调
    failure_callback = None
    if req.config:
        # 根据配置创建回调函数
        config_dict = req.config.model_dump()  # 使用新的 model_dump() 方法
        failure_callback = callback_registry.create_configured_callback(config_dict)
        
        # 如果指定了邮箱，创建邮件通知回调
        if req.config.notification_email:
            email_callback = create_email_notification_callback(req.config.notification_email)
            # 如果已有配置回调，组合它们
            if failure_callback:
                original_callback = failure_callback
                async def combined_callback(failure_data):
                    await original_callback(failure_data)
                    await email_callback(failure_data)
                failure_callback = combined_callback
            else:
                failure_callback = email_callback

    task_id = task_manager.create_task(
        task_type=TaskType.ZH2EN,
        input_data={"text": req.text},
        model_name=model_name,
        use_chains=True,
        max_retries=req.config.max_retries if req.config else 3,
        failure_callback=failure_callback
    )

    logger.info(f"异步中译英任务已提交: task_id={task_id}")

    return {
        "task_id": task_id,
        "status": "submitted",
        "message": "Task submitted successfully",
        "poll_url": f"/api/translate/async/status/{task_id}",
        "result_url": f"/api/translate/async/result/{task_id}",
    }


@router.post("/en2zh")
async def submit_async_en2zh_task(
    req: SimpleTextRequest,
):
    """
    提交异步英译中任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    # 验证输入
    if not req.text or not req.text.strip():
        raise EmptyTextError()
    
    model_name = (getattr(req, 'model', None) or "").strip() or None
    task_id = task_manager.create_task(
        task_type=TaskType.EN2ZH,
        input_data={"text": req.text},
        model_name=model_name,
        use_chains=True,
    )

    return {
        "task_id": task_id,
        "status": "submitted",
        "message": "Task submitted successfully",
        "poll_url": f"/api/translate/async/status/{task_id}",
        "result_url": f"/api/translate/async/result/{task_id}",
    }


@router.post("/summarize")
async def submit_async_summarize_task(
    req: SimpleTextRequest,
    max_length: int = Query(200, description="总结最大长度"),
):
    """
    提交异步总结任务
    返回任务ID，客户端可使用此ID轮询结果
    """
    try:
        model_name = (getattr(req, 'model', None) or "").strip() or None
        task_id = task_manager.create_task(
            task_type=TaskType.SUMMARIZE,
            input_data={"text": req.text, "max_length": max_length},
            model_name=model_name,
            use_chains=True,
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}",
            "result_url": f"/api/translate/async/result/{task_id}",
        }

    except Exception as e:
        logger.error(f"Failed to submit summarize task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keyword-summary")
async def submit_async_keyword_summary_task(
    req: SimpleTextRequest,
    summary_length: int = Query(100, description="总结长度"),
):
    """
    提交异步关键词总结任务
    """
    try:
        model_name = (getattr(req, 'model', None) or "").strip() or None
        task_id = task_manager.create_task(
            task_type=TaskType.KEYWORD_SUMMARY,
            input_data={"text": req.text, "summary_length": summary_length},
            model_name=model_name,
            use_chains=True,
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}",
            "result_url": f"/api/translate/async/result/{task_id}",
        }

    except Exception as e:
        logger.error(f"Failed to submit keyword summary task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/structured-summary")
async def submit_async_structured_summary_task(
    req: SimpleTextRequest,
    max_length: int = Query(300, description="总结最大长度"),
):
    """
    提交异步结构化总结任务
    """
    try:
        model_name = (getattr(req, 'model', None) or "").strip() or None
        task_id = task_manager.create_task(
            task_type=TaskType.STRUCTURED_SUMMARY,
            input_data={"text": req.text, "max_length": max_length},
            model_name=model_name,
            use_chains=True,
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "poll_url": f"/api/translate/async/status/{task_id}",
            "result_url": f"/api/translate/async/result/{task_id}",
        }

    except Exception as e:
        logger.error(f"Failed to submit structured summary task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    用于轮询任务进度和结果
    """
    task_status = task_manager.get_task_status(task_id)

    if not task_status:
        raise TaskNotFoundException(task_id)

    return task_status


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """
    获取任务结果
    仅返回已完成任务的结果
    """
    result = task_manager.get_task_result(task_id)

    if not result:
        raise TaskNotFoundException(task_id)

    return result


@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    取消正在执行的任务
    """
    success = task_manager.cancel_task(task_id)

    if not success:
        raise TaskNotFoundException(task_id)

    return {"message": f"Task {task_id} has been cancelled"}


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="过滤任务状态 (pending, running, completed, failed, expired)"),
    limit: int = Query(50, description="返回任务数量限制"),
):
    """
    列出所有任务
    支持按状态过滤
    """
    try:
        filter_status = None
        if status:
            try:
                filter_status = TaskStatus(status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        tasks = task_manager.list_tasks(status=filter_status)

        if limit > 0:
            tasks = tasks[:limit]

        return {"tasks": tasks, "total": len(tasks), "filtered_by": status}

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_async_stats():
    """
    获取异步任务系统统计信息
    """
    try:
        all_tasks = task_manager.list_tasks()

        stats = {
            "total_tasks": len(all_tasks),
            "by_status": {},
            "by_type": {},
            "system_info": {
                "max_concurrent_tasks": task_manager.max_concurrent_tasks,
                "active_tasks": len([t for t in all_tasks if t["status"] == "running"]),
            },
        }

        for task in all_tasks:
            st = task["status"]
            stats["by_status"][st] = stats["by_status"].get(st, 0) + 1

        for task in all_tasks:
            t = task["task_type"]
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

        return stats

    except Exception as e:
        logger.error(f"Failed to get async stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 便捷别名：直接用 task_id 查询
@router.get("/{task_id}")
async def get_task_by_id(
    task_id: str = Path(..., description="任务ID（UUID）", pattern=r"^[0-9a-fA-F-]{36}$")
):
    """
    便捷接口：
    - 如果任务已完成，直接返回结果（等价于 GET /result/{task_id}）
    - 如果未完成，返回当前状态并给出轮询与结果链接
    - 如果不存在，返回 404
    这样可支持 GET /api/translate/async/{task_id} 的直觉式查询。
    """
    # 优先尝试返回结果
    result = task_manager.get_task_result(task_id)
    if result:
        return result

    # 返回状态与指导链接
    status_info = task_manager.get_task_status(task_id)
    if status_info:
        return {
            "message": "Task not completed yet",
            "status": status_info.get("status"),
            "task_id": task_id,
            "poll_url": f"/api/translate/async/status/{task_id}",
            "result_url": f"/api/translate/async/result/{task_id}",
        }

    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/callbacks/available")
async def list_available_callbacks():
    """
    列出所有可用的失败回调函数
    """
    return {
        "available_callbacks": callback_registry.list_available(),
        "description": {
            "log_failure": "记录失败信息到日志",
            "save_failure_details": "保存失败详情到文件", 
            "send_notification": "发送失败通知",
            "cleanup_task_data": "清理失败任务数据",
            "slack_notification": "发送 Slack 通知（需配置）",
            "database_log": "记录失败信息到数据库（需配置）"
        }
    }


@router.post("/callbacks/test")
async def test_failure_callback(
    callback_name: str = Query(..., description="要测试的回调函数名称")
):
    """
    测试失败回调函数
    """
    callback = callback_registry.get(callback_name)
    if not callback:
        raise HTTPException(status_code=404, detail=f"Callback '{callback_name}' not found")
    
    # 创建测试失败数据
    from datetime import datetime
    test_failure_data = {
        "task_id": "test-task-123",
        "task_type": "zh2en",
        "error_message": "This is a test failure",
        "error_traceback": "Test traceback",
        "retry_count": 1,
        "max_retries": 3,
        "input_data": {"text": "测试文本"},
        "created_at": datetime.now(),
        "failed_at": datetime.now()
    }
    
    try:
        await callback(test_failure_data)
        return {
            "message": f"Callback '{callback_name}' executed successfully",
            "callback_name": callback_name
        }
    except Exception as e:
        logger.error(f"Error testing callback '{callback_name}': {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Callback test failed: {str(e)}"
        )
