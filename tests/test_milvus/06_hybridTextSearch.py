from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient, DataType, Function, FunctionType
from pymilvus import AnnSearchRequest
from openai import OpenAI
import json



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 混合搜索
# 初始化Embeddings客户端
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b", base_url="http://8.155.174.96:11434")
print("Embeddings客户端初始化成功")

# 2、实例化Milvus客户端对象
client = MilvusClient(
    uri="http://8.155.174.96:19530",
    db_name="milvus_database"
)
print("Milvus客户端初始化成功")

# 3、定义文本embedding处理函数
def emb_text(text):
    return embeddings.embed_query(text)

# 4、混合搜索
question = "AI智能体是否能预测未来？"
# 定义第一个搜索参数 基本 ANN 搜索请求
search_param_1 = {
    "data": [emb_text(question)],
    "anns_field": "content_dense",
    "param": {"nprobe": 10, "metric_type": "COSINE"},
    "limit": 2,
}
# 定义第二个搜索参数 全文搜索请求
search_param_2 = {
    "data": [question],
    "anns_field": "title_sparse",
    "param": {"drop_ratio_search": 0.2},
    "limit": 2
}
# 在混合搜索中，每个AnnSearchRequest 只支持一个查询数据
request_1 = AnnSearchRequest(**search_param_1)
request_2 = AnnSearchRequest(**search_param_2)
# 互惠排名融合（RRF）排名器是 Milvus 混合搜索的一种重新排名策略，它根据多个向量搜索路径的排名位置而不是原始相似度得分来平衡搜索结果
# RRF Ranker 专门设计用于混合搜索场景，在这种场景中，您需要平衡来自多个向量搜索路径的结果，而无需分配明确的重要性权重
RRFRanker = Function(
    name="rrf",
    input_field_names=[],
    function_type=FunctionType.RERANK,
    params={
        "reranker": "rrf",
        "k": 100
    }
)
# 加权排名器通过为每个搜索路径分配不同的重要性权重，智能地组合来自多个搜索路径的结果并确定其优先级
# 使用加权排名策略时，需要输入权重值。输入权重值的数量应与混合搜索中基本 ANN 搜索请求的数量一致
# 输入的权重值范围应为 [0,1]，数值越接近 1 表示重要性越高
WeightRanker = Function(
    name="weight",
    input_field_names=[],
    function_type=FunctionType.RERANK,
    params={
        "reranker": "weighted",
        "weights": [0.1, 0.9],
        # 是否在加权前对原始分数进行归一化处理
        "norm_score": True
    }
)
# 执行混合搜索
res = client.hybrid_search(
    collection_name="my_collection_demo_chunked",
    reqs=[request_1, request_2],
    ranker=RRFRanker,
    # ranker=WeightRanker,
    limit=2,
    output_fields=["title", "content_chunk", "link", "pubAuthor"]
)
print(f"res:{res}")