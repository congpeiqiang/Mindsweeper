"""
监督代理 - 使用LangGraph自带supervisor
负责协调各个专门代理的工作流程
pip install langgraph-supervisor
"""
from langchain.agents import create_agent
from langchain.messages  import  RemoveMessage, HumanMessage
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

from app.agents.chat_to_db_agents.chart_generator_agent import chart_generator_agent

"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

"""

from typing import Dict, Any, List

from app.core.state import SQLMessageState, UserContext
from app.core.llms import get_default_model


def _some_logic_messages(request, runtime):
    if len(runtime.state["messages"]) > 0 and hasattr(runtime.state["messages"][-1], "tool_calls") and runtime.state["messages"][-1].tool_calls[0]['name'] == "schema_agent":
        RemoveMessage(id=runtime.state["messages"][-1].id)
    runtime.state["messages"].append(HumanMessage(content=request))


class SupervisorAgent:
    """监督代理 - 基于LangGraph自带supervisor"""

    def __init__(self, worker_agents: List[Any] = None):
        self.llm = get_default_model()
        self.tools = self._create_worker_agents_tool()
        self.supervisor = self._create_supervisor()

    def _create_worker_agents_tool(self) -> List[Any]:
        """创建工作代理"""
        from app.agents.chat_to_db_agents.schema_agent import schema_agent
        # from app.agents.chat_to_db_agents.sample_retrieval_agent import sample_retrieval_agent
        from app.agents.chat_to_db_agents.sql_generator_agent import sql_generator_agent
        from app.agents.chat_to_db_agents.sql_validator_agent import sql_validator_agent
        from app.agents.chat_to_db_agents.sql_executor_agent import sql_executor_agent
        # from app.agents.chat_to_db_agents.error_recovery_agent import error_recovery_agent
        # from app.agents.chat_to_db_agents.chart_generator_agent import chart_generator_agent

        @tool("schema_agent")
        async def schema_agent_tool(request: str, runtime: ToolRuntime[UserContext]) -> Command:
            """
            分析用户查询，获取相关数据库表结构
            :param runtime:
            :param request:
            :return:
            """
            user_context = runtime.context
            tool_call_id=runtime.tool_call_id
            # return Command(update={"messages": [ToolMessage(content="111", tool_call_id=tool_call_id)]})
            print(f"Supervisor Agent Tool({tool_call_id}): 执行Schema Agent")
            state = runtime.state
            result = await schema_agent.agent.ainvoke(
                {"messages": [{"role": "user", "content": request}],
                 # "schema_info": state["schema_info"],
                 # "query_analysis": state["query_analysis"],
                 # "generated_sql": state["generated_sql"],
                 # "validation_result": state["validation_result"],
                 # "execution_result": state["execution_result"],
                 # "sample_retrieval_result": state["sample_retrieval_result"],
                 # "retry_count": state["retry_count"],
                 # "max_retries": state["max_retries"],
                 # "current_stage": state["current_stage"],
                 # "error_history": state["error_history"],
                 },
                context=user_context
            )
            # if len(result["messages"])>0 and isinstance(result["messages"][-1], AIMessage):
            #     result["agent_messages"] = state["agent_messages"]
            #     result["agent_messages"].append({"schema_agent":result["messages"][-1]})
            # del result["messages"]
            # del state["messages"]
            # print("%%%%%%%%%")
            # print(result)
            # print("(((((((((((((((((((((((((")
            # print(state)
            # state.update(result)
            # print("&&&&&&&&&&&&")
            # print(state)
            state["agent_messages"]=[{"supervisor agent call schema agent tool": HumanMessage(request)}, {"schema_agent":result["messages"][-1]}]
            state["messages"]=[ToolMessage(content=result["messages"][-1].content, tool_call_id=tool_call_id)]
            # 更新state，除了agent_messages和messages
            # state.update({k: v for k, v in result.items() if k not in ['messages', 'agent_messages']})
            state.update({k: v for k, v in result.items() if k in ['query_analysis', 'schema_info', 'current_stage', 'error_history']})
            return Command(update=state)

        @tool(name_or_callable="sql_generator_agent")
        async def sql_generator_agent_tool(request: str, runtime: ToolRuntime[UserContext]) -> Command:
            """
            根据模式信息和样本生成高质量SQL语句
            :param runtime:
            :param request:
            :return:
            """
            user_context = runtime.context
            tool_call_id = runtime.tool_call_id
            print(f"Supervisor Agent Tool({tool_call_id}): 执行Sql Generator Agent")
            state = runtime.state
            result = await sql_generator_agent.agent.ainvoke(
                {"messages": [{"role": "user", "content": request}],
                 "schema_info": state["schema_info"],
                 "query_analysis": state["query_analysis"],
                 # "generated_sql": state["generated_sql"],
                 # "validation_result": state["validation_result"],
                 # "execution_result": state["execution_result"],
                 "sample_retrieval_result": state["sample_retrieval_result"],
                 "retry_count": state["retry_count"],
                 "max_retries": state["max_retries"],
                 "current_stage": state["current_stage"],
                 "error_history": state["error_history"],
                 },
                context=user_context
            )
            state["messages"] = [ToolMessage(content=result["messages"][-1].content, tool_call_id=tool_call_id)]
            state["agent_messages"] = [{"supervisor agent call sql generator agent tool": HumanMessage(request)}, {"sql_generator_agent": result["messages"][-1]}]
            # state.update({k: v for k, v in result.items() if k not in ['messages', 'agent_messages']})
            state.update({k: v for k, v in result.items() if k in ['generated_sql', 'current_stage', 'error_history']})
            return Command(update=state)

        @tool(name_or_callable="sql_validator_agent")
        async def sql_validator_agent_tool(request: str, runtime: ToolRuntime[UserContext]) -> Command:
            """
            验证SQL的语法、安全性和性能
            :param runtime:
            :param request:
            :return:
            """
            user_context = runtime.context
            tool_call_id = runtime.tool_call_id
            print(f"Supervisor Agent Tool({tool_call_id}): 执行Sql Validator Agent")
            state = runtime.state
            result = await sql_validator_agent.agent.ainvoke(
                {"messages": [{"role": "user", "content": request}],
                 "schema_info": state["schema_info"],
                 "query_analysis": state["query_analysis"],
                 "generated_sql": state["generated_sql"],
                 # "validation_result": state["validation_result"],
                 # "execution_result":state["execution_result"],
                 "sample_retrieval_result": state["sample_retrieval_result"],
                 "retry_count": state["retry_count"],
                 "max_retries": state["max_retries"],
                 "current_stage": state["current_stage"],
                 "error_history": state["error_history"],
                 },
                context=user_context
            )
            print(f"sql_validator_agent_tool result:\n {result}")
            state["messages"] = [ToolMessage(content=result["messages"][-1].content, tool_call_id=tool_call_id)]
            state["agent_messages"] = [{"supervisor agent call sql generator agent tool": HumanMessage(request)},
                                       {"sql_generator_agent": result["messages"][-1]}]
            state.update({k: v for k, v in result.items() if k in ['validation_result', 'current_stage', 'error_history']})
            return Command(update=state)

        @tool(name_or_callable="sql_executor_agent")
        async def sql_executor_agent_tool(request: str, runtime: ToolRuntime[UserContext]) -> Command:
            """
            安全执行SQL并返回结果
            :param runtime:
            :param request:
            :return:
            """
            user_context = runtime.context
            tool_call_id = runtime.tool_call_id
            print(f"Supervisor Agent Tool({tool_call_id}): 安全执行SQL并返回结果")
            state = runtime.state
            result = await sql_executor_agent.agent.ainvoke(
                {"messages": [{"role": "user", "content": request}],
                 "schema_info": state["schema_info"],
                 "query_analysis": state["query_analysis"],
                 # "generated_sql": state["generated_sql"],
                 "validation_result": state["validation_result"],
                 # "execution_result": state["execution_result"],
                 "sample_retrieval_result": state["sample_retrieval_result"],
                 "retry_count": state["retry_count"],
                 "max_retries": state["max_retries"],
                 "current_stage": state["current_stage"],
                 "error_history": state["error_history"],
                 },
                context=user_context
            )
            state["messages"] = [ToolMessage(content=result["messages"][-1].content, tool_call_id=tool_call_id)]
            state["agent_messages"] = [{"supervisor agent call sql generator agent tool": HumanMessage(request)},
                                       {"sql_generator_agent": result["messages"][-1]}]
            # state.update({k: v for k, v in result.items() if k not in ['messages', 'agent_messages']})
            state.update({k: v for k, v in result.items() if k in ['execution_result', 'current_stage', 'error_history']})
            return Command(update=state)

        @tool(name_or_callable="chart_generator_agent")
        async def chart_generator_agent_tool(request: str, runtime: ToolRuntime[UserContext]) -> Command:
            """
            1. 分析SQL查询结果数据的特征和结构
            2. 判断是否需要生成图表
            3. 推荐最适合的图表类型
            4. 生成高质量的数据可视化图表
            :param runtime:
            :param request:
            :return:
            """
            user_context = runtime.context
            tool_call_id = runtime.tool_call_id
            print(f"Supervisor Agent Tool({tool_call_id}): 绘制图表")
            state = runtime.state
            result = await chart_generator_agent.agent.ainvoke(
                {"messages": [{"role": "user", "content": request}],
                 "schema_info": state["schema_info"],
                 "query_analysis": state["query_analysis"],
                 "generated_sql": state["generated_sql"],
                 # "validation_result": state["validation_result"],
                 # "execution_result": state["execution_result"],
                 "sample_retrieval_result": state["sample_retrieval_result"],
                 "retry_count": state["retry_count"],
                 "max_retries": state["max_retries"],
                 "current_stage": state["current_stage"],
                 "error_history": state["error_history"],
                 },
                context=user_context
            )
            state["messages"] = [ToolMessage(content=result["messages"][-1].content, tool_call_id=tool_call_id)]
            state["agent_messages"] = [{"supervisor agent call sql generator agent tool": HumanMessage(request)},
                                       {"sql_generator_agent": result["messages"][-1]}]
            state.update({k: v for k, v in result.items() if k not in ['messages', 'agent_messages']})
            return Command(update=state)

        # 返回agent对象而不是包装类
        return [
            schema_agent_tool,
            sql_generator_agent_tool,
            sql_validator_agent_tool,
            sql_executor_agent_tool,
            chart_generator_agent_tool
        ]


    def _create_supervisor(self):
        """创建LangGraph supervisor"""
        print("=== 创建LangGraph supervisor ===")
        supervisor = create_agent(
            self.llm,
            state_schema=SQLMessageState,
            tools=self.tools,
            context_schema=UserContext,
            system_prompt=self._get_supervisor_prompt(),
        )
        return supervisor

    # 📚 ** sample_retrieval_agent **: 检索相关的SQL问答对样本，提供高质量参考
    # sample_retrieval_agent →

    # ** 样本检索优化: **
    # - 基于用户查询语义检索相似问答对
    # - 结合数据库结构进行结构化匹配
    # - 提供高质量SQL生成参考样本
    def _get_supervisor_prompt(self) -> str:
        system_msg = f"""你是一个智能的SQL Agent系统监督者。
你管理以下专门代理：

🔍 **schema_agent**: 分析用户查询，获取相关数据库表结构
⚙️ **sql_generator_agent**: 根据模式信息和样本生成高质量SQL语句
🔍 **sql_validator_agent**: 验证SQL的语法、安全性和性能
🚀 **sql_executor_agent**: 安全执行SQL并返回结果
📊 **chart_generator_agent**: 根据查询结果生成数据可视化图表
🔧 **error_recovery_agent**: 处理错误并提供修复方案

**工作原则:**
1. 根据当前任务阶段选择合适的代理
2. 确保工作流程的连续性和一致性
3. 智能处理错误和异常情况
4. 一次只分配给一个代理，不要并行调用
5. 不要自己执行任何具体工作

**标准流程:**
用户查询 → schema_agent → sql_generator_agent → sql_validator_agent → sql_executor_agent → chart_generator_agent → 完成

**图表生成条件:**
- 用户查询包含可视化意图（如"图表"、"趋势"、"分布"、"比较"等关键词）
- 查询结果包含数值数据且适合可视化
- 数据量适中（2-1000行）


**错误处理:**
任何阶段出错 → error_recovery_agent → 重试相应阶段

请根据当前状态和任务需求做出最佳的代理选择决策。特别注意：
- 当用户查询包含可视化意图时，在SQL执行完成后应考虑调用chart_generator_agent
- 当查询结果适合可视化时，主动建议生成图表"""

        return system_msg

    async def supervise(self, state: SQLMessageState, user_context:UserContext) -> Dict[str, Any]:
        """监督整个流程"""
        try:
            result = await self.supervisor.ainvoke(
                state,
                config={"recursion_limit": 16},
                context=user_context
            )
            return {
                "success": True,
                "result": result
            }
        except NotImplementedError as e:
            print(e)
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e)
            }


# def create_supervisor_agent(worker_agents: List[Any] = None) -> SupervisorAgent:
#     """创建监督代理实例"""
#     return SupervisorAgent(worker_agents)

def create_intelligent_sql_supervisor() -> SupervisorAgent:
    """创建智能SQL监督代理的便捷函数"""
    return SupervisorAgent()
