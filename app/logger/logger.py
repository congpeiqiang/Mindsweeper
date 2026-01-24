#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :  logger.py
@Author  :  CongPeiQiang
@Time    :  2025/7/24 21:14
@Desc    :  改进的日志记录器，避免日志记录导致主线程挂起
"""
import logging
import os
import queue
import threading
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
from pathlib import Path

# from concurrent_log import ConcurrentTimedRotatingFileHandler

class AppLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name: str = "src", log_dir: str = "logs", log_name: str = "log.log", level: int = logging.INFO):
        # 读取环境变量
        # furnaceId = os.getenv('furnaceId', None)
        # if furnaceId:
        #     print("ERROR: 环境变量中 furnaceId 未设置!")
        # log_dir = "/data/logs/"
        # log_dir = "data/logs/"
        # 避免重复初始化
        if hasattr(self, 'initialized'):
            return

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 创建日志队列
        self.log_queue = queue.Queue()

        # 确保日志目录存在
        self.log_dir = log_dir
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 检查文件权限
        self._check_log_dir()

        # 设置处理器
        self._setup_handlers(log_name)

        # 标记已初始化
        self.initialized = True

    def _check_log_dir(self):
        """检查日志目录是否可写"""
        try:
            test_file = os.path.join(self.log_dir, "test.log")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            print(f"警告: 无法写入日志目录 {self.log_dir}, 错误: {e}")
            self.log_dir = None

    def _setup_handlers(self, log_name: str):
        """设置日志处理器"""
        # 清除现有处理器
        self.logger.handlers.clear()

        # 创建队列处理器
        queue_handler = QueueHandler(self.log_queue)
        self.logger.addHandler(queue_handler)

        # 创建监听器处理器列表
        handlers = []

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter())
        handlers.append(console_handler)

        # # 文件处理器（如果日志目录可用）
        # if self.log_dir:
        #     try:
        #         # 每天重新创建一个日志文件，最多保留backup_count份
        #         file_handler = ConcurrentTimedRotatingFileHandler(
        #             filename=os.path.join(self.log_dir, log_name),
        #             when="MIDNIGHT",
        #             interval=1,
        #             backupCount=5,
        #             delay=True,
        #             encoding="utf-8")
        #         file_handler.setFormatter(self._get_formatter())
        #         handlers.append(file_handler)
        #     except Exception as e:
        #             print(f"警告: 无法创建文件日志处理器, 错误: {e}")

        # 文件处理器（如果日志目录可用）
        if self.log_dir:
            try:
                file_handler = TimedRotatingFileHandler(
                    filename=os.path.join(self.log_dir, log_name),
                    when='midnight',
                    interval=1,
                    backupCount=5,
                    encoding="utf-8",
                    utc=False,
                    delay=False  # 改为 False,立即创建日志文件
                )
                file_handler.suffix = "%Y-%m-%d.log"
                file_handler.setFormatter(self._get_formatter())
                handlers.append(file_handler)
            except Exception as e:
                print(f"警告: 无法创建文件日志处理器, 错误: {e}")

        # 创建并启动监听器
        self.listener = QueueListener(self.log_queue, *handlers)
        self.listener.start()

    def _get_formatter(self) -> logging.Formatter:
        """获取日志格式化器"""
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
        )

    def get_logger(self) -> logging.Logger:
        """获取日志记录器"""
        return self.logger

    def shutdown(self):
        """关闭日志记录器"""
        if hasattr(self, 'listener'):
            self.listener.stop()


# 使用示例
# if __name__ == '__main__':
#     # 创建日志记录器
#     logger = AppLogger(
#         name=os.path.basename(__file__),
#         log_dir="test_logs",
#         log_name="test-logs.log",
#         level=logging.DEBUG
#     ).get_logger()
#
#     try:
#         # 记录不同级别的日志
#         logger.debug("这是一条调试信息")
#         logger.info("这是一条信息")
#         logger.warning("这是一条警告")
#         logger.error("这是一条错误")
#         logger.critical("这是一条严重错误")
#
#         # 测试带参数的日志
#         value = 42
#         logger.debug(f"变量的值是: {value}")
#
#         # 测试异常日志
#         try:
#             1 / 0
#         except Exception as e:
#             logger.error("捕获到异常", exc_info=True)
#
#     finally:
#         # 确保在程序退出前关闭日志记录器
#         logger.__class__._instance.shutdown()
