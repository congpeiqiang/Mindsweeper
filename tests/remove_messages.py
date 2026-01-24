#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/9 14:14
# @Author  : CongPeiQiang
# @File    : remove_messages.py
# @Software: PyCharm
from langchain.messages  import  RemoveMessage, HumanMessage,AIMessage



state={"messages":[
    HumanMessage(content="111", id="111"),
    AIMessage(content="222", id="222"),
    HumanMessage(content="333", id="333")]
}
print(state)

# print({"messages": [RemoveMessage(id=m.id) for m in state["messages"][:2]]})
state={"messages": [RemoveMessage(id=m.id) for m in state["messages"][:2]]}
print(state)