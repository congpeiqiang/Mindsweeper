"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
load_dotenv()

# def get_default_model(tools: Optional[list] = None):
#     model = ChatDeepSeek(model="deepseek-chat", max_tokens=8192, temperature=0.2)
#     # if tools:
#     #     model.bind_tools(tools, parallel_tool_calls=True)
#     return model

def get_default_model(tools: Optional[list] = None):
    model = init_chat_model(model="deepseek-chat", model_provider="deepseek",max_tokens=8192, temperature=0.2)
    if tools:
        model.bind_tools(tools, parallel_tool_calls=True)
    return model