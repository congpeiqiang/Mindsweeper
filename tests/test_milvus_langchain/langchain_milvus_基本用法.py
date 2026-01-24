"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""
from langchain_community.vectorstores import Milvus
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(
    model="qwen3-embedding:0.6b",
    base_url="http://47.120.44.223:11434",
    temperature=0
)
# ss = """
#
#
# """
# embedding.embed_query(ss)
# doc_splits=["",""]
# embedding.embed_documents(doc_splits)

URI = "http://47.120.44.223:19530"

# 初始化
vector_store = Milvus(
    collection_name="myapp_db",
    embedding_function=embedding,
    connection_args={"uri": URI},
    index_params={"index_type": "FLAT", "metric_type": "L2"},
)

# 添加document
from uuid import uuid4

from langchain_core.documents import Document

document_1 = Document(
    page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

document_3 = Document(
    page_content="Building an exciting new project with LangChain - come check it out!",
    metadata={"source": "tweet"},
)

document_4 = Document(
    page_content="Robbers broke into the city bank and stole $1 million in cash.",
    metadata={"source": "news"},
)

document_5 = Document(
    page_content="Wow! That was an amazing movie. I can't wait to see it again.",
    metadata={"source": "tweet"},
)

document_6 = Document(
    page_content="Is the new iPhone worth the price? Read this review to find out.",
    metadata={"source": "website"},
)

document_7 = Document(
    page_content="The top 10 soccer players in the world right now.",
    metadata={"source": "website"},
)

document_8 = Document(
    page_content="LangGraph is the best framework for building stateful, agentic applications!",
    metadata={"source": "tweet"},
)

document_9 = Document(
    page_content="The stock market is down 500 points today due to fears of a recession.",
    metadata={"source": "news"},
)

document_10 = Document(
    page_content="I have a bad feeling I am going to get deleted :(",
    metadata={"source": "tweet"},
)

documents = [
    document_1,
    document_2,
    document_3,
    document_4,
    document_5,
    document_6,
    document_7,
    document_8,
    document_9,
    document_10,
]
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store.add_documents(documents=documents, ids=uuids)

# 从Milvus存储中删除document
vector_store.delete(ids=["uuid1", "uuid2"])

# 相似性搜索 返回document列表
results = vector_store.similarity_search(
    "LangChain provides abstractions to make working with LLMs easy",
    k=2,
    expr='source == "tweet"',
    # param=...  # Search params for the index type
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")

# 根据分数进行相似性搜索
results = vector_store.similarity_search_with_score(
    "Will it be hot tomorrow?", k=1, expr='source == "news"'
)
for res, score in results:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")

# 通过转化为检索器进行查询
retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1, "fetch_k": 5, "lambda_mult": 0.5})
retriever.invoke("Stealing from the bank is a crime", expr='source == "news"')

# 为许多不同的用户存储数据，而且这些用户不能查看彼此的数据 https://milvus.io/docs/zh/multi_tenancy.md#Partition-key-based-multi-tenancy


