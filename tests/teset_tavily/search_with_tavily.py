# _*_ coding:utf-8_*_
from typing import Dict, Any


def _format_search_results(results: Dict[str, Any]) -> str:
    """格式化搜索结果"""
    formatted = ""
    if "results" in results:
        for i, result in enumerate(results["results"], 1):
            formatted += f"\n### 结果 {i}\n"
            formatted += f"**标题**: {result.get('title', 'N/A')}\n"
            formatted += f"**链接**: {result.get('url', 'N/A')}\n"
            formatted += f"**摘要**: {result.get('content', 'N/A')}\n"
    return formatted

def search_with_tavily(keyword: str) -> tuple:
    """
    使用Tavily进行搜索

    Returns:
        (formatted_results, result_count) 元组
    """
    try:
        import requests

        # 调用Tavily API
        api_key = "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"
        url = "https://api.tavily.com/search"

        payload = {
            "api_key": api_key,
            "query": keyword,
            "max_results": 10
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        results = response.json()

        formatted_results = _format_search_results(results)
        result_count = len(results.get("results", []))
        return formatted_results, result_count
    except Exception as e:
        print(f"warning: Tavily搜索失败，返回默认结果: {e}")
        return f"搜索关键字: {keyword}\n\n（搜索服务暂时不可用）", 0

search_result = search_with_tavily("langchain")