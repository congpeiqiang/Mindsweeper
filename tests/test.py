#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/9 16:49
# @Author  : CongPeiQiang
# @File    : test.py
# @Software: PyCharm

import re
import json
response_text="""json
{
    "entities": ["教师表", "学生表", "关系表"],
    "relationships": ["教师与学生之间的教学关系", "教师表与学生表通过关系表关联"],
    "query_intent": "统计教师总数，并计算每位教师所教的学生数量",
    "likely_aggregations": ["count"],
    "time_related": false,
    "comparison_related": false
}
"""
# 提取并解析JSON响应
json_match = re.search(r'\{[\s\S]*}', response_text)
if json_match:
    json_str = json_match.group(0)
    print(json_str)
    analysis = json.loads(json_str)
    print(type(analysis), analysis)


from pathlib import Path
file_path = r"D:\workspace\huice\Mindsweeper\upload\旅行日记.pdf"
size_bytes = Path(file_path).stat().st_size
print(size_bytes)