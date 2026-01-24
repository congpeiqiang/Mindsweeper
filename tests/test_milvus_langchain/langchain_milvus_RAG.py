# _*_ coding:utf-8_*_
# https://milvus.io/docs/zh/integrate_with_langchain.md
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

vectorstore = Milvus.from_documents(
    documents=docs,
    embedding=embeddings,
    connection_args={
        "uri": "./milvus_demo.db",
    },
    drop_old=False,  # Drop the old Milvus collection if it exists
)

query = "What is self-reflection of an AI Agent?"
vectorstore.similarity_search(query, k=1)
"""
[Document(page_content='Self-Reflection#\nSelf-reflection is a vital aspect that allows autonomous agents to improve iteratively by refining past action decisions and correcting previous mistakes. It plays a crucial role in real-world tasks where trial and error are inevitable.\nReAct (Yao et al. 2023) integrates reasoning and acting within LLM by extending the action space to be a combination of task-specific discrete actions and the language space. The former enables LLM to interact with the environment (e.g. use Wikipedia search API), while the latter prompting LLM to generate reasoning traces in natural language.\nThe ReAct prompt template incorporates explicit steps for LLM to think, roughly formatted as:\nThought: ...\nAction: ...\nObservation: ...\n... (Repeated many times)', metadata={'source': 'https://lilianweng.github.io/posts/2023-06-23-agent/', 'pk': 449281835035555859})]
"""



# 元数据过滤  更加metadata中的字段过滤
vectorstore.similarity_search(
    "What is CoT?",
    k=1,
    expr="source == 'https://lilianweng.github.io/posts/2023-06-23-agent/'",
)


# 动态传入元数据过滤  更加metadata中的字段过滤
from langchain_core.runnables import ConfigurableField

retriever2 = vectorstore.as_retriever().configurable_fields(
    search_kwargs=ConfigurableField(
        id="retriever_search_kwargs",
    )
)
rag_chain2 = (
    {"context": retriever2 | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
rag_chain2.with_config(
    configurable={
        "retriever_search_kwargs": dict(
            expr="source == 'https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/'",
        )
    }
).invoke(query)


