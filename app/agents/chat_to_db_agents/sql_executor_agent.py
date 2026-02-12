"""
SQL执行代理
负责安全地执行SQL查询并处理结果
"""

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.types import Command

from app.core.state import SQLExecutionResult

"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Dict, Any
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from langchain.messages import ToolMessage
from app.core.llms import get_default_model


@tool
def execute_sql_query(sql_query: str, runtime:ToolRuntime) -> Dict[str, Any]:
    """
    执行SQL查询

    Args:
        sql_query: SQL查询语句
        connection_id: 数据库连接ID
        timeout: 超时时间（秒）

    Returns:
        查询执行结果
    """
    print("Tool: 执行SQL查询")
    try:
        connection_id = getattr(runtime.context, "connection_id", None)
        # 根据connection_id获取数据库连接并执行查询
        from app.services.test_to_sql.db_service import get_db_connection_by_id, execute_query_with_connection

        # 获取数据库连接
        connection = get_db_connection_by_id(connection_id)
        if not connection:
            return {
                "success": False,
                "error": f"找不到连接ID为 {connection_id} 的数据库连接"
            }

        # 执行查询
        result_data = execute_query_with_connection(connection, sql_query)
        print(f"Tool: 执行SQL查询结果: {result_data}; \nsql: {sql_query}")
        """
        success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    rows_affected: Optional[int] = None
        """
        sql_execution_result = SQLExecutionResult(**{
            "success": True,
            "data": result_data,
            "error": None,
            "execution_time": 0,  # TODO: 添加执行时间计算
            "rows_affected": len(result_data)
        })
        tool_call_id = runtime.tool_call_id
        tool_message = ToolMessage(name="validate_sql_syntax", content=sql_execution_result.model_dump_json(),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "execution_result": [SQLExecutionResult],
                               "current_stage": "sql_execution"})
        # return {
        #     "success": True,
        #     "data": {
        #         "columns": list(result_data[0].keys()) if result_data else [],
        #         "data": [list(row.values()) for row in result_data],
        #         "row_count": len(result_data),
        #         "column_count": len(result_data[0].keys()) if result_data else 0
        #     },
        #     "error": None,
        #     "execution_time": 0,  # TODO: 添加执行时间计算
        #     "rows_affected": len(result_data)
        # }

    except Exception as e:
        tool_message = ToolMessage(name="execute_sql_query", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message],
                               "error_history": [{"sql_executor_agent:tool:execute_sql_query": str(e)}],
                               "current_stage": "sql_execution"})
        # return {
        #     "success": False,
        #     "error": str(e),
        #     "execution_time": 0
        # }


@tool
def analyze_query_performance(sql_query: str, execution_result: Dict[str, Any], runtime:ToolRuntime) -> Dict[str, Any]:
    """
    分析查询性能
    
    Args:
        sql_query: SQL查询语句
        execution_result: 执行结果
        
    Returns:
        性能分析结果
    """
    print("Tool: 分析查询性能")
    try:
        execution_time = execution_result.get("execution_time", 0)
        row_count = execution_result.get("rows_affected", 0)
        
        # 性能评估
        performance_rating = "excellent"
        if execution_time > 5:
            performance_rating = "poor"
        elif execution_time > 2:
            performance_rating = "fair"
        elif execution_time > 1:
            performance_rating = "good"
        
        # 生成性能建议
        suggestions = []
        if execution_time > 2:
            suggestions.append("查询执行时间较长，考虑添加索引或优化查询")
        if row_count > 10000:
            suggestions.append("返回行数较多，考虑添加分页或更严格的过滤条件")

        sql_execution_result = SQLExecutionResult(**{
            "success": True,
            "error": None,
            "performance_rating": performance_rating,
            "execution_time": execution_time,
            "row_count": row_count,
            "suggestions": suggestions
        })
        tool_call_id = runtime.tool_call_id
        tool_message = ToolMessage(name="validate_sql_syntax", content=sql_execution_result.model_dump_json(),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "execution_result": [SQLExecutionResult],
                               "current_stage": "sql_execution"})
        
        # return {
        #     "success": True,
        #     "performance_rating": performance_rating,
        #     "execution_time": execution_time,
        #     "row_count": row_count,
        #     "suggestions": suggestions
        # }
        
    except Exception as e:
        tool_message = ToolMessage(name="analyze_query_performance", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message],
                               "error_history": [{"sql_executor_agent:tool:analyze_query_performance": str(e)}],
                               "current_stage": "sql_execution"})


@tool
def format_query_results(runtime:ToolRuntime, execution_result: Dict[str, Any], format_type: str = "table") -> Dict[str, Any]:
    """
    格式化查询结果
    
    Args:
        execution_result: 执行结果
        format_type: 格式类型 (table, json, csv)
        
    Returns:
        格式化后的结果
    """
    print("Tool: 格式化查询结果")
    try:
        if not execution_result.get("success"):
            return execution_result
        
        data = execution_result.get("data", {})
        columns = data.get("columns", [])
        rows = data.get("data", [])
        
        if format_type == "table":
            # 创建表格格式
            if not columns or not rows:
                formatted_result = "查询结果为空"
            else:
                # 创建简单的表格格式
                header = " | ".join(columns)
                separator = "-" * len(header)
                row_strings = []
                for row in rows[:10]:  # 限制显示前10行
                    row_str = " | ".join(str(cell) for cell in row)
                    row_strings.append(row_str)
                
                formatted_result = f"{header}\n{separator}\n" + "\n".join(row_strings)
                if len(rows) > 10:
                    formatted_result += f"\n... 还有 {len(rows) - 10} 行"
        
        elif format_type == "json":
            # JSON格式
            if columns and rows:
                json_data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    json_data.append(row_dict)
                formatted_result = json_data
            else:
                formatted_result = []
        
        elif format_type == "csv":
            # CSV格式
            if columns and rows:
                csv_lines = [",".join(columns)]
                for row in rows:
                    csv_line = ",".join(str(cell) for cell in row)
                    csv_lines.append(csv_line)
                formatted_result = "\n".join(csv_lines)
            else:
                formatted_result = ""
        
        else:
            formatted_result = str(data)

        sql_execution_result = SQLExecutionResult(**{
            "success": True,
            "error": None,
            "formatted_result": formatted_result,
            "format_type": format_type,
            "original_data": data
        })
        tool_call_id = runtime.tool_call_id
        tool_message = ToolMessage(name="validate_sql_syntax", content=sql_execution_result.model_dump_json(),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "execution_result": [SQLExecutionResult],
                               "current_stage": "sql_execution"})
        
        # return {
        #     "success": True,
        #     "formatted_result": formatted_result,
        #     "format_type": format_type,
        #     "original_data": data
        # }
        
    except Exception as e:
        tool_message = ToolMessage(name="format_query_results", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message],
                               "error_history": [{"sql_executor_agent:tool:format_query_results": str(e)}],
                               "current_stage": "sql_execution"})


@dynamic_prompt
def create_system_prompt(request: ModelRequest) -> str:
    context = request.runtime.context
    connection_id = getattr(context, "connection_id", None)
    """创建系统提示"""
    system_msg = f"""你是一个专业的SQL执行专家。
        **重要：当前数据库connection_id是 {connection_id}**
        你的任务是：
            1. 安全地执行SQL查询
            2. 分析查询性能
            3. 格式化查询结果

            执行流程：
            使用 execute_sql_query 执行SQL查询

            执行原则：
            - 确保查询安全性
            - 监控执行性能
            - 提供清晰的结果展示
            - 处理执行错误

            如果执行失败，请提供详细的错误信息和解决建议。
"""
    return system_msg

class SQLExecutorAgent:
    """SQL执行代理"""

    def __init__(self):
        self.name = "sql_executor_agent"  # 添加name属性
        self.tools = [execute_sql_query]    # [analyze_query_performance, format_query_results]
        self.llm = get_default_model([execute_sql_query])
        # 创建ReAct代理
        self.agent = create_agent(
            self.llm,
            self.tools,
            middleware=[create_system_prompt],
            name=self.name
        )
# 创建全局实例
sql_executor_agent = SQLExecutorAgent()
