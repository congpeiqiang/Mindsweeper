"""
智能SQL代理图 - 高级接口和图构建
专注于图的构建和便捷接口，supervisor逻辑委托给SupervisorAgent
"""
from langchain_core.messages import HumanMessage

"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Dict, Any

from app.core.state import SQLMessageState, UserContext
from app.agents.chat_to_db_agents.supervisor_agent import create_intelligent_sql_supervisor


def extract_connection_id_from_messages(messages) -> int:
    """从消息中提取连接ID"""
    print(f"=== 提取连接ID ===")
    print(f"消息数量: {len(messages) if messages else 0}")

    connection_id = 15  # 默认值

    # 查找最新的人类消息中的连接ID
    for message in reversed(messages):
        if hasattr(message, 'type') and message.type == 'human':
            if hasattr(message, 'additional_kwargs') and message.additional_kwargs:
                msg_connection_id = message.additional_kwargs.get('connection_id')
                if msg_connection_id:
                    connection_id = msg_connection_id
                    print(f"从消息中找到连接ID: {connection_id}")
                    break

    print(f"最终使用的连接ID: {connection_id}")
    print("==================")
    return connection_id


class IntelligentSQLGraph:
    """智能SQL代理图 - 高级接口"""

    def __init__(self):
        # 使用SupervisorAgent来处理所有supervisor逻辑
        self.supervisor_agent = create_intelligent_sql_supervisor()
        self.graph = self.supervisor_agent.supervisor

    async def process_query(self, query: str, connection_id: int = 15) -> Dict[str, Any]:
        """处理SQL查询"""
        try:
            # 初始化状态
            initial_state = SQLMessageState(
                messages=[HumanMessage(query)],
                agent_messages=[{"supervisor_agent": HumanMessage(query)}],
                query_analysis=None,
                schema_info=None,
                generated_sql=[],
                validation_result=[],
                execution_result=[],
                sample_retrieval_result=None,
                current_stage="schema_analysis",
                retry_count=0,
                max_retries=3,
                error_history=[]
            )
            # 委托给supervisor处理
            result = await self.supervisor_agent.supervise(initial_state, user_context=UserContext(connection_id=connection_id))
            print(f"Supervisor返回结果: {result}")
            if result.get("success"):
                return {
                    "success": True,
                    "result": result.get("result"),
                    "final_stage": result.get("result", {}).get("current_stage", "completed")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "final_stage":  result.get("final_stage", "error"),
                    "result": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_stage": "error"
            }

# 便捷函数
def create_intelligent_sql_graph() -> IntelligentSQLGraph:
    """创建智能SQL图实例"""
    return IntelligentSQLGraph()

async def process_sql_query(query: str, connection_id: int = 15) -> Dict[str, Any]:
    """处理SQL查询的便捷函数"""
    graph = create_intelligent_sql_graph()
    return await graph.process_query(query, connection_id)

# 创建全局实例（为了向后兼容）
_global_graph = None

def get_global_graph():
    """获取全局图实例"""
    global _global_graph
    if _global_graph is None:
        _global_graph = create_intelligent_sql_graph()
    return _global_graph

graph = get_global_graph().graph


# if __name__ == "__main__":
#     # 创建图实例
#     graph_instance = create_intelligent_sql_graph()
#     # print(f"智能SQL图创建成功: {type(graph_instance).__name__}")
#     print(f"智能SQL图创建成功: {graph_instance.__class__.__name__}")
#     print(f"Supervisor代理: {type(graph_instance.supervisor_agent).__name__}")
#     print(f"工作代理数量: {len(graph_instance.worker_agents)}")
