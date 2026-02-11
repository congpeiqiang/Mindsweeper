"""
Schema分析代理
负责分析用户查询并获取相关的数据库模式信息
"""
import json

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.config import get_stream_writer
from langgraph.prebuilt import ToolRuntime


"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""
from langgraph.types import Command
from typing import Dict, Any
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from app.core.state import SQLMessageState, UserContext, update_query_analysis, update_error_history, SchemaInfo
from app.core.llms import get_default_model
from app.db.session import SessionLocal
from app.services.test_to_sql.text2sql_utils import retrieve_relevant_schema, get_value_mappings, analyze_query_with_llm

@tool
def analyze_user_query(query: str, runtime: ToolRuntime[SQLMessageState]) -> Command:
    """
    分析用户的自然语言查询，提取关键实体和意图
    
    Args:
        :param query: 用户的自然语言查询
        :param runtime:
    Returns:
        包含实体、关系和查询意图的分析结果
    """
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Schema Agent({tool_call_id}): 分析用户的自然语言查询，提取关键实体和意图...")
    state = runtime.state
    try:
        analysis = analyze_query_with_llm(query)
        query_analysis = update_query_analysis(state, query_analysis={query:analysis})
        tool_message = ToolMessage(name="analyze_user_query", content=json.dumps(query_analysis, ensure_ascii=False), tool_call_id=tool_call_id)
        return Command(update={"messages":[tool_message], "query_analysis": query_analysis, "current_stage": "schema_analysis"})
    except Exception as e:
        tool_message = ToolMessage(name="retrieve_database_schema", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        # error_history = update_error_history(state, error_history=[{"schema_agent:tool:analyze_user_query": str(e)}])
        return Command(update={"messages":[tool_message], "error_history": [{"schema_agent:tool:analyze_user_query": str(e)}], "current_stage": "schema_analysis"})

@tool
def retrieve_database_schema(query: str, runtime: ToolRuntime[UserContext, SQLMessageState]) -> Command:
    """
    根据查询分析结果获取相关的数据库表结构信息
    Args:
        query: 用户查询
        :param query:
        :param runtime  数据库连接ID

    Returns:
        相关的表结构和值映射信息
    """

    writer = get_stream_writer()
    connection_id = getattr(runtime.context, "connection_id", None)
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Schema Agent({tool_call_id}): 根据查询分析结果获取相关的数据库表结构信息...", f"connection_id: {connection_id}")
    writer(f"Tool of Schema Agent-writer({tool_call_id}): 根据查询分析结果获取相关的数据库表结构信息...{connection_id}")
    if connection_id is None:
        return Command(update={"error_history": [{"schema_agent:tool:retrieve_database_schema": "connection_id is not set in runtime context"}], "current_stage": "schema_analysis"})
    state = runtime.state
    try:
        db = SessionLocal()
        try:
            # 获取相关表结构
            schema_context = retrieve_relevant_schema(
                db=db,
                connection_id=connection_id,
                query=query
            )
            
            # 获取值映射
            value_mappings = get_value_mappings(db, schema_context)
            tables = schema_context.get("tables", {})
            relationships = schema_context.get("relationships", [])
            # schema_info = update_schema_info(state, schema_info={"tables": tables, "value_mappings": value_mappings, "relationships": relationships})
            schema_info = SchemaInfo(tables=tables, value_mappings=value_mappings, relationships=relationships)
            tool_message = ToolMessage(name="retrieve_database_schema", content=schema_info.model_dump_json(),
                                       tool_call_id=tool_call_id)
            return Command(update={"messages":[tool_message], "schema_info": [schema_info], "current_stage": "schema_analysis"})
        finally:
            db.close()
    except Exception as e:
        tool_message = ToolMessage(name="retrieve_database_schema", content="Calling the tool produced no output.",
                                       tool_call_id=tool_call_id)
        # error_history = update_error_history(state, error_history=[{"schema_agent:tool:retrieve_database_schema": str(e)}])
        return Command(update={"messages":[tool_message], "error_history": [{"schema_agent:tool:retrieve_database_schema": str(e)}], "current_stage": "schema_analysis"})


@tool
def validate_schema_completeness(schema_info: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证获取的模式信息是否足够完整来回答用户查询
    
    Args:
        schema_info: 获取的模式信息
        query_analysis: 查询分析结果
        
    Returns:
        验证结果和建议
    """
    try:
        # 检查是否有足够的表信息
        required_entities = query_analysis.get("entities", [])
        available_tables = list(schema_info.get("schema_context", {}).keys())
        
        missing_entities = []
        for entity in required_entities:
            # 简单的匹配逻辑，可以进一步优化
            if not any(entity.lower() in table.lower() for table in available_tables):
                missing_entities.append(entity)
        
        is_complete = len(missing_entities) == 0
        
        suggestions = []
        if missing_entities:
            suggestions.append(f"可能缺少与以下实体相关的表信息: {', '.join(missing_entities)}")
        
        return {
            "success": True,
            "is_complete": is_complete,
            "missing_entities": missing_entities,
            "suggestions": suggestions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@dynamic_prompt
def create_system_prompt(request: ModelRequest) -> str:
    # context = request.runtime.context
    # connection_id = context.get("connection_id", None)
    # ** 重要：当前数据库connection_id是{connection_id} **
    """创建系统提示"""
    system_msg = f"""你是一个专业的数据库模式分析专家。
你的任务是：
1. 分析用户的自然语言查询，理解其意图和涉及的实体
2. 获取与查询相关的数据库表结构信息
3. 验证获取的模式信息是否足够完整

工作流程：
1. 首先使用 analyze_user_query 工具分析用户查询
2. 然后使用 retrieve_database_schema 工具获取相关表结构

请确保：
- 准确理解用户查询意图
- 获取所有相关的表和字段信息
- 包含必要的值映射信息
- 验证信息的完整性

如果发现信息不完整，请提供具体的建议。"""
    return system_msg

class SchemaAnalysisAgent:
    """Schema分析代理"""

    def __init__(self):
        self.name = "schema_agent"  # 添加name属性
        self.llm = get_default_model()
        self.tools = [analyze_user_query, retrieve_database_schema] #, validate_schema_completeness]

        # 创建ReAct代理
        self.agent = create_agent(
            state_schema=SQLMessageState,
            model=self.llm,
            tools=self.tools,
            context_schema=UserContext,
            middleware=[create_system_prompt],
            name=self.name,
        )


# 创建全局实例
schema_agent = SchemaAnalysisAgent()
