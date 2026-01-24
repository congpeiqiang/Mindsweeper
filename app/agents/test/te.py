#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/8 15:18
# @Author  : CongPeiQiang
# @File    : te.py
# @Software: PyCharm
from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek
load_dotenv()

@dynamic_prompt
def user_role_prompt(request: ModelRequest):
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."
    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."
    return base_prompt

# context此处只支持TypedDict
class UserContext(TypedDict):
    user_role: str

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model=model,
                     middleware=[user_role_prompt],
                     context_schema=UserContext)
results = agent.invoke({"messages": [HumanMessage("Explain machine learning")]},
             context={"user_role": "expert"})
for result in results["messages"]:
    print(result)