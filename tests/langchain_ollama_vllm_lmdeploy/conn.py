"""
@File    :  conn.py
@Author  :  CongPeiQiang
@Time    :  2026/3/10 22:35
@Desc    :  
"""
# 首先安装必要的包

from langchain.chat_models import init_chat_model

# --- 1. 接入 Ollama (使用原生 ollama provider) ---
# 注意：ollama 的 base_url 默认就是 http://localhost:11434，通常无需指定
# ollama_llm = init_chat_model(
#     model="qwen3:0.6b",  # 你在 ollama 中下载的模型名
#     model_provider="ollama",
#     temperature=0.7,
#     base_url="http://localhost:11434" # 可选，如果需要自定义地址可以加上
# )

# --- 2. 接入 vLLM (使用 openai provider) ---
# vllm_llm = init_chat_model(
#     model="/root/autodl-tmp/model/Qwen/Qwen3-0___6B", # vLLM 启动时指定的模型名(例如: vllm启动的本地模型,则此处也配置模型路径)
#     model_provider="openai",
#     base_url="http://localhost:8000/v1",  # vLLM 的地址
#     api_key="EMPTY",                       # vLLM 通常不校验 key
#     temperature=0.7
# )

# --- 3. 接入 LMDeploy (也使用 openai provider) ---
lmdeploy_llm = init_chat_model(
    model="/root/autodl-tmp/model/Qwen/Qwen3-0___6B",   # LMDeploy 部署的模型名
    model_provider="openai",
    base_url="http://localhost:23333/v1",   # LMDeploy 的地址
    api_key="EMPTY",
    temperature=0.7
)

# --- 调用方式完全一致 ---
from langchain_core.messages import HumanMessage

messages = [HumanMessage(content="你是谁")]

# 随便选一个模型调用
# response = ollama_llm.invoke(messages)
# print(response.content)

# 也可以试试 vLLM 的
# response = vllm_llm.invoke(messages)
# print(response.content)

# 也可以试试 lmdeploy 的
response = lmdeploy_llm.invoke(messages)
print(response.content)