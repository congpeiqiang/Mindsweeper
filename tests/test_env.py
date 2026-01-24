#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/3 14:28
# @Author  : CongPeiQiang
# @File    : test_env.py
# @Software: PyCharm

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import get_settings

# 获取配置实例
settings = get_settings()

# 访问 .env 中的配置
print(settings.APP_NAME)  # 知识库管理系统
print(settings.DEBUG)  # True
print(settings.MILVUS_HOST)  # 8.155.174.96
print(settings.CORS_ORIGINS_LIST)  # ['http://localhost:3000', 'http://localhost:8080']

import json
security_issues=[]
json.dumps({"is_secure": len(security_issues) == 0,"security_issues": security_issues})