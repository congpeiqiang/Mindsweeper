"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from fastapi import APIRouter

from app.config.settings import get_settings
from app.api.v1.endpoints.notebook import documents

settings = get_settings()

from app.api.v1.endpoints.test_to_sql import graph_visualization, query, connections, relationship_tips, schema, \
    hybrid_qa, value_mappings

# 强制重新加载 - 修复API路由问题

api_router = APIRouter()

# ==================== 健康检查端点 ====================

@api_router.get("/health", tags=["health"], summary="健康检查")
async def health_check():
    """
    健康检查端点

    Returns:
        健康状态信息
    """
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        },
    }

# ==================== 根路由 ====================
# 添加API根路径处理器
@api_router.get("/", tags=["root"], summary="根路由")
async def api_root():
    """API根路径"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "connections": "/api/v1/connections/",
            "schema": "/api/v1/schema/",
            "query": "/api/v1/query/",
            "value_mappings": "/api/v1/value-mappings/",
            "graph_visualization": "/api/v1/graph-visualization/",
            "relationship_tips": "/api/v1/relationship-tips/",
            "hybrid_qa": "/api/v1/hybrid-qa/",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "redoc_url": "/redoc",
        }
    }

# # ========== 处理 OPTIONS 请求 ==========
# @api_router.options("/connections")
# async def options_handler() -> Response:
#     """处理所有 OPTIONS 预检请求"""
#     headers = {
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Methods": "*",
#         "Access-Control-Allow-Headers": "*",
#         "Access-Control-Max-Age": "86400",  # 24小时
#     }
#     return Response(content="CORS preflight successful", headers=headers, status_code=200)

# text_to_sql
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(schema.router, prefix="/schema", tags=["schema"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(value_mappings.router, prefix="/value-mappings", tags=["value-mappings"])
api_router.include_router(graph_visualization.router, prefix="/graph-visualization", tags=["graph-visualization"])
api_router.include_router(relationship_tips.router, prefix="/relationship-tips", tags=["relationship-tips"])
api_router.include_router(hybrid_qa.router, prefix="/hybrid-qa", tags=["hybrid-qa"])

# notebook
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

