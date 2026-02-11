#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/30 09:45
# @Author  : CongPeiQiang
# @File    : Ragas_langchain.py
# @Software: PyCharm
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient
from dotenv import load_dotenv
load_dotenv()

URI = "http://47.120.44.223:19530"

embedding = OllamaEmbeddings(
    model="qwen3-embedding:0.6b",
    base_url="http://47.120.44.223:11434",
    temperature=0
)

client = MilvusClient(
    uri="http://47.120.44.223:19530",
    db_name="milvus_database"
)

def _retriver_context(query:str):
    docs_content = ""
    query_vector = embedding.embed_query(query)
    retrieved_docs = client.search(
        collection_name="my_collection_1",
        data=[query_vector],
        anns_field="content_dense",
        output_fields=["chunk_index", "content_chunk"],
        limit=2,
    )
    """
    data: [[{'id': 463338387081398685, 'distance': 0.25868040323257446, 'entity': {'content_chunk': '相比于没有推理能力加持、只会做简单说话和重复性动作的模型方...\n除了高动态场景，还是需要细腻情感表达的独白，模型都能拿捏，展现出了表演张力。\n\n双系统框架为虚拟人装上「大脑」\n\n近年来，视频虚拟人技术发展迅猛，从最初的口型合成，进化到了半身乃至全身的动画生成。', 'chunk_index': 0}}]]
    """
    if len(retrieved_docs) != 0:
        for docs in retrieved_docs:
            for doc in docs:
                docs_content += doc.get('entity', {}).get("content_chunk", "") + "\n"
    return docs_content

@dynamic_prompt
def prompt_with_context(request: ModelRequest):
    last_query = request.state["messages"][-1].text
    docs_content = _retriver_context(last_query)
    if len(docs_content) == 0:
        docs_content = "未检索到上下文"
        system_message = (
            "You are a helpful assistant. Use the following context in your response:"
            f"\n\n{docs_content}"
        )
    else:
        system_message = (
            "You are a helpful assistant. Use the following context in your response:"
            f"\n\n{docs_content}"
        )
    return system_message

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model=model,
                     middleware=[prompt_with_context]
                     )

from datasets import Dataset
question = ["大家的目标是什么？"]
ground_truth = ["创造一个与真人无异，既能理性行动又能真实表达情感的「数字生命」"]
answer = []
contexts = []

for query in question:
    # response = agent.invoke({"messages": HumanMessage(query)})
    # answer.append(response["messages"][-1].content)
    answer.append("等欸发欸你风格")
    contexts.append([_retriver_context(query)])

data = {
    "question":question,
    "answer":answer,
    "ground_truth":ground_truth,
    "contexts":contexts
}

dataset = Dataset.from_dict(data)
print(dataset)
"""
Dataset({
    features: ['question', 'answer', 'ground_truth', 'contexts'],
    num_rows: 1
})
"""

from ragas import evaluate
from ragas.metrics import (
    _faithfulness,
    _answer_relevancy,
    _context_recall,
    _context_precision
)

result = evaluate(
    dataset = dataset,
    metrics = [
        _faithfulness
    ]

)
print(result)