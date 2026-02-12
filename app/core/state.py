"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""
import operator
from pydoc import describe

from typing import Dict, Any, List, Optional, Literal, NotRequired, TypedDict, Required, Annotated
from pydantic import Field

from langchain.agents import AgentState
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from pydantic import BaseModel

class SchemaInfo(BaseModel):
    """数据库模式信息"""
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    value_mappings: Dict[str, Dict[str, str]] = Field(default_factory=dict)

class SQLValidationResult(BaseModel):
    """SQL验证结果"""
    success: bool
    sql_name: str
    is_valid: bool = Field(default=True)
    is_secure: bool = Field(default=True)
    security_issues: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class SQLExecutionResult(BaseModel):
    """SQL执行结果"""
    success: bool
    data: Optional[Any] = Field(default=None, description="sql执行结果数据")
    error: Optional[str] = Field(default=None)
    execution_time: Optional[float] = Field(default=None)
    rows_affected: Optional[int] = Field(default=None)
    formatted_result: Optional[str] = Field(default=None)
    format_type: Optional[str] = Field(default=None)
    performance_rating: Optional[str] = Field(default=None)
    original_data: data
    row_count: Optional[int] = Field(default=None)
    suggestions: Optional[list] = []

    class Config:
        arbitrary_types_allowed = True


class SQLMessageState(AgentState):
    """增强的SQL消息状态，支持多代理协作"""

    # 查询分析结果
    query_analysis: Annotated[list[Dict[str, Any]], operator.add]

    # 模式信息
    schema_info: Optional[SchemaInfo]

    # 生成的SQL
    generated_sql: Annotated[list[str], operator.add]

    # SQL验证结果
    validation_result: Annotated[list[SQLValidationResult], operator.add]

    # 执行结果
    execution_result: Annotated[list[SQLExecutionResult], operator.add]

    # 样本检索结果
    sample_retrieval_result: Optional[Dict[str, Any]]

    # 错误重试计数
    retry_count: int
    max_retries: int

    # 当前处理阶段
    current_stage: Literal[
        "schema_analysis",
        "sample_retrieval",
        "sql_generation",
        "sql_validation",
        "sql_execution",
        "error_recovery",
        "completed"
    ]

    messages: Annotated[list[BaseMessage], add_messages]
    # 代理间通信
    agent_messages: Annotated[list[Dict[str, Any]], operator.add]

    # 错误历史
    error_history: Annotated[list[Dict[str, Any]], operator.add]

from pydantic import BaseModel


class UserContext(BaseModel):
    connection_id: int


# def update_query_analysis(state: dict, **kwargs):
#     query_analysis_new = kwargs.get("query_analysis", None)
#     if query_analysis_new is not None and "query_analysis" in state and state["query_analysis"] is not None:
#         try:
#             query_analysis_old = state["query_analysis"]
#             query_analysis_old.update(query_analysis_new)
#             return query_analysis_old
#         except Exception as e:
#             print(f"Error updating query_analysis: {e}")
#     else:
#         return query_analysis_new

# def update_schema_info(state: dict, **kwargs):
#     schema_info_new = kwargs.get("schema_info", None)
#     if schema_info_new is not None and "schema_info" in state and state["schema_info"] is not None:
#         try:
#             schema_info_old = state["schema_info"]
#             schema_info_old.update(schema_info_new)
#             return schema_info_old
#         except Exception as e:
#             print(f"Error updating query_analysis: {e}")
#     else:
#         return schema_info_new

# def update_error_history(state: dict, **kwargs):
#     error_history_new = kwargs.get("error_history", None)
#     if error_history_new is not None and "error_history" in state and isinstance(state["error_history"], list):
#         error_history_old = state["error_history"]
#         error_history_old.append(error_history_new)
#         return error_history_old
#     else:
#         return error_history_new

# def update_messages(state: dict, **kwargs):
#     messages_new = kwargs.get("messages", None)
#     if messages_new is not None and "messages" in state and isinstance(state["messages"], list):
#         messages_old = state["messages"]
#         messages_old.append(messages_new)
#         return messages_old
#     elif messages_new is None:
#         return state["messages"]
#     else:
#         return messages_new

# def update_SQLMessageState(state: dict, **kwargs):
#     query_analysis = kwargs.get("query_analysis", None)
#     if query_analysis is not None and "query_analysis" in state and state["query_analysis"] is not None:
#         try:
#             state["query_analysis"].update(query_analysis)
#         except Exception as e:
#             print(f"Error updating query_analysis: {e}")
#     else:
#         state["query_analysis"] = query_analysis
#
#     schema_info = kwargs.get("schema_info", None)
#     if schema_info is not None and "schema_info" in state:
#         state["schema_info"] = schema_info
#
#     generated_sql = kwargs.get("generated_sql", None)
#     if generated_sql is not None and "generated_sql" in state:
#         state["generated_sql"] = generated_sql
#
#     validation_result = kwargs.get("validation_result", None)
#     if validation_result is not None and "validation_result" in state:
#         state["validation_result"] = validation_result
#
#     execution_result = kwargs.get("execution_result", None)
#     if execution_result is not None and "execution_result" in state:
#         state["execution_result"] = execution_result
#
#     sample_retrieval_result = kwargs.get("sample_retrieval_result", None)
#     if sample_retrieval_result is not None and "sample_retrieval_result" in state:
#         state["sample_retrieval_result"] = sample_retrieval_result
#
#     retry_count = kwargs.get("retry_count", False)
#     if retry_count is True and "retry_count" in state and state["retry_count"] is not None:
#         state["retry_count"] += retry_count
#     else:
#         state["retry_count"] = retry_count
#
#     current_stage = kwargs.get("current_stage", None)
#     if current_stage is not None and "current_stage" in state:
#         state["current_stage"] = current_stage
#
#     agent_messages = kwargs.get("agent_messages", None)
#     if agent_messages is not None and  "agent_messages" in state and isinstance(state["agent_messages"], list):
#         state["agent_messages"].append(agent_messages)
#     else:
#         state["agent_messages"] = agent_messages
#
#     error_history = kwargs.get("error_history", None)
#     if error_history is not None and "error_history" in state and isinstance(state["error_history"], list):
#         state["error_history"].append(error_history)
#     else:
#         state["error_history"] = error_history