# _*_ coding:utf-8_*_

"""
FastAPI 的 BackgroundTasks 允许在请求响应后执行后台任务，非常适合处理不需要立即返回结果的操作。
"""

# 基本示例
from fastapi import FastAPI, BackgroundTasks
from typing import Optional
import time

app = FastAPI(
    title="fastapi_BackgroundTasks",
    version="v1.1.0",
    description="fastapi_BackgroundTasks",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


def write_log(message: str):
    time.sleep(2)  # 模拟耗时操作
    with open("log.txt", mode="a") as log:
        log.write(f"{message}\n")
    print(f"日志已写入: {message}")


@app.post("/send-notification/")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    # 添加到后台任务
    background_tasks.add_task(write_log, f"发送邮件给 {email}")

    return {"message": "通知已发送", "email": email}


def process_data(data: dict, priority: int = 1):
    time.sleep(3)
    print(f"处理数据: {data}, 优先级: {priority}")


@app.post("/process/")
async def process_endpoint(
        data: dict,
        priority: int,
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    print(data)
    # 添加带多个参数的任务
    background_tasks.add_task(process_data, data, priority)

    # 添加多个任务
    background_tasks.add_task(write_log, f"开始处理数据: {data}")

    return {"status": "processing", "data_id": id(data)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_BackgroundTasks:app",
        host="0.0.0.0",
        port=8002,
        access_log=True,
        timeout_keep_alive=120
    )