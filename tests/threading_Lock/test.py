#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/31 14:01
# @Author  : CongPeiQiang
# @File    : test.py
# @Software: PyCharm

import threading
import time

# 创建一个锁
lock = threading.Lock()
shared_resource = 0

def worker():
    global shared_resource
    for _ in range(100000):
        with lock:  # 自动获取和释放锁
            # 临界区 - 安全地修改共享资源
            shared_resource += 1
            print(shared_resource)

# 创建多个线程
threads = []
for i in range(5):
    t = threading.Thread(name=f"threading_{i}", target=worker)
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

print(f"Final value: {shared_resource}")  # 应该是 500000