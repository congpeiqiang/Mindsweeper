#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/11/22 15:46
# @Author  : CongPeiQiang
# @File    : test.py
# @Software: PyCharm
import asyncio

from app.agents.chat_to_db_agents.chat_graph import process_sql_query

# 处理自然语言查询
result = asyncio.run(process_sql_query(
    query="查询有多少老师，及每个老师教多少学生？，最后绘制图表。",
    connection_id=12
))
print("最终返回结果: \n", result)