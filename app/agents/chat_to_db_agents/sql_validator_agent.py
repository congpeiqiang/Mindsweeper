"""
SQL验证代理
负责验证生成的SQL语句的正确性、安全性和性能
"""
import json

from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import re
import sqlparse
from typing import Dict, Any, List
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

from app.core.state import SQLMessageState, SQLValidationResult, update_error_history
from app.core.llms import get_default_model


@tool
def validate_sql_syntax(sql_query: str, runtime = ToolRuntime) -> Command:
    """
    验证SQL语法正确性
    
    Args:
        :param sql_query: SQL查询语句
        :param runtime:
        
    Returns:
        语法验证结果
    """
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Validate Sql Syntax({tool_call_id}): 验证SQL语法正确性;\n sql: {sql_query}")
    state = runtime.state
    try:
        errors = []
        warnings = []
        # 使用sqlparse进行基础语法检查
        try:
            parsed = sqlparse.parse(sql_query)
            if not parsed:
                errors.append("SQL语句无法解析")
        except Exception as e:
            errors.append(f"SQL语法错误: {str(e)}")
        
        # 检查常见的SQL问题
        sql_upper = sql_query.upper()
        
        # 检查是否包含危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                errors.append(f"包含危险操作: {keyword}")
        
        # 检查是否有SELECT语句
        if 'SELECT' not in sql_upper:
            errors.append("缺少SELECT语句")
        
        # 检查括号匹配
        if sql_query.count('(') != sql_query.count(')'):
            errors.append("括号不匹配")
        
        # 检查引号匹配
        single_quotes = sql_query.count("'")
        double_quotes = sql_query.count('"')
        if single_quotes % 2 != 0:
            warnings.append("单引号可能不匹配")
        if double_quotes % 2 != 0:
            warnings.append("双引号可能不匹配")
        
        # 检查是否有LIMIT子句（推荐）
        if 'LIMIT' not in sql_upper and 'TOP' not in sql_upper:
            warnings.append("建议添加LIMIT子句以限制结果集大小")
        if len(errors)==0:
            validation_result=True
        else:
            validation_result=False
        validation_result_final = SQLValidationResult(**{
            "sql_name": "validate_sql_syntax",
            "success": True,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        })
        tool_message = ToolMessage(name="validate_sql_syntax", content=validation_result_final.model_dump_json(), tool_call_id=tool_call_id)
        return Command(update={"messages":[tool_message], "validation_result": [validation_result_final], "current_stage": "sql_validation"})
        
    except Exception as e:
        tool_message = ToolMessage(name="validate_sql_syntax", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        error_history = update_error_history(state,error_history={"sql_validator_agent:tool:validate_sql_syntax": str(e)})
        return Command(update={"messages":[tool_message], "error_history": error_history, "current_stage": "sql_validation"})

@tool
def validate_sql_security(sql_query: str, runtime:ToolRuntime) -> Command:
    """
    验证SQL安全性，检查SQL注入风险

    Args:
        :param sql_query: SQL查询语句
        :param runtime:
        
    Returns:
        安全性验证结果
    """
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Sql Validator Agent(validate_sql_security): 验证SQL安全性，检查SQL注入风险; \nsql: {sql_query}")
    state = runtime.state
    try:
        security_issues = []
        warnings = []
        
        # 检查SQL注入模式
        injection_patterns = [
            r"';.*--",  # 注释注入
            r"union.*select",  # UNION注入
            r"or.*1=1",  # 逻辑注入
            r"and.*1=1",  # 逻辑注入
            r"exec\s*\(",  # 执行函数
            r"sp_",  # 存储过程
            r"xp_",  # 扩展存储过程
        ]
        
        sql_lower = sql_query.lower()
        for pattern in injection_patterns:
            if re.search(pattern, sql_lower):
                security_issues.append(f"检测到潜在的SQL注入模式: {pattern}")
        
        # 检查动态SQL构造
        if "concat" in sql_lower or "||" in sql_query:
            warnings.append("检测到字符串拼接，请确保输入已正确转义")
        
        # 检查用户输入直接嵌入
        if "'" in sql_query and not re.search(r"'[^']*'", sql_query):
            warnings.append("检测到可能的未转义用户输入")

        validation_result_final = SQLValidationResult(**{
            "sql_name": "validate_sql_security",
            "success": True,
            "is_secure": len(security_issues) == 0,
            "security_issues": security_issues,
            "warnings": warnings
        })
        tool_message = ToolMessage(name="validate_sql_security", content=str(validation_result_final),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "validation_result": validation_result_final,
                               "current_stage": "sql_validation"})
        
    except Exception as e:
        error_history = update_error_history(state, error_history={"sql_validator_agent:tool:validate_sql_security": str(e)})
        tool_message = ToolMessage(name="validate_sql_security", content=f"call validate_sql_security error: {e}",
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "error_history": error_history, "current_stage": "sql_validation"})


@tool
def validate_sql_performance(sql_query: str, runtime:ToolRuntime) -> Command:
    """
    验证SQL性能，识别潜在的性能问题

    Args:
        :param sql_query: SQL查询语句
        :param runtime:
        
    Returns:
        性能验证结果
    """
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Sql Validator Agent(validate_sql_performance): Tool: 验证SQL性能，识别潜在的性能问题; {sql_query}")
    state = runtime.state
    # 建议调用数据库的性能测试工具：mysql的 explain ，改造一下

    try:
        performance_issues = []
        suggestions = []
        
        sql_upper = sql_query.upper()
        
        # 检查是否使用SELECT *
        if re.search(r'SELECT\s+\*', sql_upper):
            performance_issues.append("使用SELECT *可能影响性能，建议明确指定需要的列")
        
        # 检查是否有WHERE子句
        if 'WHERE' not in sql_upper and 'LIMIT' not in sql_upper:
            performance_issues.append("缺少WHERE子句可能导致全表扫描")
        
        # 检查JOIN类型
        if 'CROSS JOIN' in sql_upper:
            performance_issues.append("CROSS JOIN可能产生笛卡尔积，影响性能")
        
        # 检查子查询
        subquery_count = sql_query.count('(SELECT')
        if subquery_count > 2:
            suggestions.append(f"检测到{subquery_count}个子查询，考虑使用JOIN优化")
        
        # 检查ORDER BY
        if 'ORDER BY' in sql_upper and 'LIMIT' not in sql_upper:
            suggestions.append("ORDER BY without LIMIT可能影响性能")
        
        # 检查LIKE模式
        like_patterns = re.findall(r"LIKE\s+'([^']*)'", sql_upper)
        for pattern in like_patterns:
            if pattern.startswith('%'):
                performance_issues.append(f"LIKE模式'{pattern}'以通配符开头，无法使用索引")
        validation_result_final = SQLValidationResult(**{
            "sql_name":"validate_sql_performance",
            "success": True,
            "performance_score": max(0, 100 - len(performance_issues) * 20),
            "performance_issues": performance_issues,
            "suggestions": suggestions
        })
        tool_message = ToolMessage(name="validate_sql_performance", content=str(validation_result_final),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "validation_result": validation_result_final,
                               "current_stage": "sql_validation"})
        
    except Exception as e:
        tool_message = ToolMessage(name="validate_sql_performance", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        error_history = update_error_history(state, error_history={"sql_validator_agent:tool:validate_sql_performance": str(e)})
        return Command(update={"messages": [tool_message], "error_history": error_history, "current_stage": "sql_validation"})


@tool
def fix_sql_issues(sql_query: str, validation_errors: List[str], runtime:ToolRuntime) -> Command:
    """
    尝试修复SQL中的问题
    
    Args:
        :param sql_query: 原始SQL查询
        :param validation_errors: 验证错误列表
        :param runtime:
        
    Returns:
        修复后的SQL和修复说明
    """
    tool_call_id = runtime.tool_call_id
    print(f"Tool of Sql Validator Agent(fix_sql_issues): Tool: 尝试修复SQL中的问题; {sql_query}; 错误列表: {validation_errors}")
    try:
        fixed_sql = sql_query
        fixes_applied = []
        
        # 修复常见问题
        for error in validation_errors:
            if "括号不匹配" in error:
                # 简单的括号修复逻辑
                open_count = fixed_sql.count('(')
                close_count = fixed_sql.count(')')
                if open_count > close_count:
                    fixed_sql += ')' * (open_count - close_count)
                    fixes_applied.append("添加缺失的右括号")
                elif close_count > open_count:
                    fixed_sql = '(' * (close_count - open_count) + fixed_sql
                    fixes_applied.append("添加缺失的左括号")
            
            elif "缺少SELECT语句" in error:
                if not fixed_sql.upper().strip().startswith('SELECT'):
                    fixed_sql = 'SELECT * FROM (' + fixed_sql + ') AS subquery'
                    fixes_applied.append("添加SELECT语句")
            
            elif "建议添加LIMIT子句" in error:
                if 'LIMIT' not in fixed_sql.upper():
                    fixed_sql += ' LIMIT 100'
                    fixes_applied.append("添加LIMIT子句")
        validation_result_final = SQLValidationResult(**{
            "sql_name":"fix_sql_issues",
            "success": True,
            "fixed_sql": fixed_sql,
            "fixes_applied": fixes_applied,
            "original_sql": sql_query
        })
        tool_message = ToolMessage(name="fix_sql_issues", content=str(validation_result_final),
                                   tool_call_id=tool_call_id)
        return Command(update={"messages": [tool_message], "validation_result": validation_result_final,
                               "current_stage": "sql_validation"})
        
    except Exception as e:
        tool_message = ToolMessage(name="fix_sql_issues", content="Calling the tool produced no output.",
                                   tool_call_id=tool_call_id)
        error_history = [{"sql_validator_agent:tool:fix_sql_issues": str(e)}]
        return Command(update={"messages": [tool_message], "error_history": error_history, "current_stage": "sql_validation"})

@tool
def human_feedback(state):
    """
    需要用户参与解决sql出现的的问题
    :param state:
    :return:
    """
    pass

class SQLValidatorAgent:
    """SQL验证代理"""

    def __init__(self):
        self.name = "sql_validator_agent"  # 添加name属性
        self.llm = get_default_model()
        self.tools = [
            validate_sql_syntax, 
            validate_sql_security, 
            validate_sql_performance, 
            fix_sql_issues
        ]
        
        # 创建ReAct代理
        self.agent = create_agent(
            state_schema=SQLMessageState,
            model=self.llm,
            tools=self.tools,
            system_prompt=self._create_system_prompt(),
            name=self.name
        )
    
    def _create_system_prompt(self) -> str:
        """创建系统提示"""
        return """你是一个专业的SQL验证专家。你的任务是：

1. 验证SQL语句的语法正确性
2. 检查SQL的安全性，防止SQL注入
3. 分析SQL的性能，识别潜在问题
4. 修复发现的问题

验证流程：
1. 使用 validate_sql_syntax 检查语法
2. 使用 validate_sql_security 检查安全性
3. 使用 validate_sql_performance 分析性能
4. 如有问题，使用 fix_sql_issues 尝试修复

验证标准：
- 语法必须正确
- 不能包含危险操作
- 应该有适当的性能优化
- 必须防止SQL注入

如果发现问题，请提供具体的修复建议。"""

# 创建全局实例
sql_validator_agent = SQLValidatorAgent()
