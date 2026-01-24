"""
定义本地工具和工具管理器

支持三种使用方式:
1. 类方法 - 无需初始化，直接调用 (推荐用于简单场景)
2. 实例方法 - 创建实例后调用 (推荐用于复杂场景)
3. 函数接口 - 向后兼容的函数式接口

支持查询所有工具，包含 MCP 工具和本地工具
"""

import logging
from typing import Any, Dict, List, Optional, Callable, cast, Union

from langchain_core.tools import BaseTool
import sqlite3

import requests
# from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class ToolsManager:
    """
    工具管理器 - 管理 SQL 数据库工具和其他本地工具

    支持类方法（无需初始化）和实例方法（需要初始化）两种使用方式。

    Class Attributes:
        DEFAULT_LLM_MODEL (str): 默认 LLM 模型
        _default_llm_model (str): 全局默认 LLM 模型
        _global_tools_cache (Dict[str, List[BaseTool]]): 全局工具缓存

    Instance Attributes:
        llm_model (str): 实例级 LLM 模型
        _tools_cache (Dict[str, List[BaseTool]]): 实例级工具缓存
    """

    # 默认 LLM 模型配置
    DEFAULT_LLM_MODEL = "deepseek:deepseek-chat"

    # 类级状态
    _default_llm_model: str = DEFAULT_LLM_MODEL
    _global_tools_cache: Dict[str, List[BaseTool]] = {}

    def __init__(self, llm_model: Optional[str] = None):
        """
        初始化工具管理器

        Args:
            llm_model: 可选的 LLM 模型名称，如果为 None 则使用默认模型
        """
        self.llm_model = llm_model or self.DEFAULT_LLM_MODEL
        self._tools_cache: Dict[str, List[BaseTool]] = {}
        logger.info(f"ToolsManager initialized with LLM model: {self.llm_model}")

    # ==================== 实例方法 ====================

    def get_sql_database_tools(self, db: Any = "sqlite:///Chinook.db") -> List[BaseTool]:
        """
        获取 SQL 数据库工具（实例方法）

        Args:
            db: 数据库连接对象

        Returns:
            SQL 数据库工具列表
        """
        cache_key = "sql_database"

        # 返回缓存的工具
        if cache_key in self._tools_cache:
            logger.debug(f"Returning cached SQL database tools")
            return self._tools_cache[cache_key]

        try:
            from langchain_community.agent_toolkits import SQLDatabaseToolkit
            from langchain.chat_models import init_chat_model

            llm = init_chat_model(self.llm_model)
            # db = SQLDatabase(db)
            db = SQLDatabase.from_uri(db)
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            tools = cast(List[BaseTool], toolkit.get_tools())

            self._tools_cache[cache_key] = tools
            logger.info(f"Loaded {len(tools)} SQL database tools")
            return tools
        except Exception as e:
            logger.error(f"Failed to load SQL database tools: {str(e)}")
            return []

    def clear_cache(self) -> None:
        """清除实例级工具缓存"""
        self._tools_cache = {}
        logger.info("Cleared instance-level tools cache")

    async def get_all_tools(
        self, db: Any = None, mcp_manager: Optional[Any] = None
    ) -> Dict[str, List[Union[BaseTool, Callable[..., Any]]]]:
        """
        获取所有工具（实例方法）- 包含本地工具和 MCP 工具

        Args:
            db: 数据库连接对象
            mcp_manager: 可选的 MCPManager 实例，用于获取 MCP 工具

        Returns:
            包含所有工具的字典，格式为:
            {
                "sql_tools": [SQL 数据库工具列表],
                "mcp_tools": {
                    "server_name": [工具列表],
                    ...
                },
                "all_tools": [所有工具的合并列表]
            }
        """
        result = {
            "sql_tools": [],
            "mcp_tools": {},
            "all_tools": [],
        }

        try:
            # 获取本地工具
            if db is not None:
                try:
                    sql_tools = self.get_sql_database_tools(db)
                    result["sql_tools"] = sql_tools
                    result["all_tools"].extend(sql_tools)
                    logger.info(f"Loaded {len(sql_tools)} local tools")
                except Exception as e:
                    logger.warning(f"Failed to load SQL tools: {str(e)}")

            # 获取 MCP 工具
            if mcp_manager is not None:
                try:
                    mcp_tools = await mcp_manager.get_all_tools()
                    result["mcp_tools"]["all"] = mcp_tools
                    result["all_tools"].extend(mcp_tools)
                    logger.info(f"Loaded {len(mcp_tools)} MCP tools")
                except Exception as e:
                    logger.warning(f"Failed to load MCP tools: {str(e)}")

            logger.info(f"Total loaded {len(result['all_tools'])} tools")
            return result
        except Exception as e:
            logger.error(f"Failed to get all tools: {str(e)}")
            return result

    # ==================== 类方法 (无需初始化) ====================

    @classmethod
    def get_sql_database_tools_cls(cls, db: Any = "sqlite:///Chinook.db") -> List[BaseTool]:
        """
        获取 SQL 数据库工具（类方法，无需初始化）

        Usage: tools = ToolsManager.get_sql_database_tools_cls(db)

        Args:
            db: 数据库连接对象

        Returns:
            SQL 数据库工具列表
        """
        cache_key = "sql_database"

        # 返回缓存的工具
        if cache_key in cls._global_tools_cache:
            logger.debug(f"Returning cached SQL database tools")
            return cls._global_tools_cache[cache_key]

        try:
            if db is None:
                logger.warning("No database connection provided, returning empty list")
                return []
            from langchain_community.agent_toolkits import SQLDatabaseToolkit
            from langchain.chat_models import init_chat_model

            llm = init_chat_model(cls._default_llm_model)
            db = SQLDatabase.from_uri(db)
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            tools = cast(List[BaseTool], toolkit.get_tools())

            cls._global_tools_cache[cache_key] = tools
            logger.info(f"Loaded {len(tools)} SQL database tools")
            return tools
        except Exception as e:
            logger.error(f"Failed to load SQL database tools: {str(e)}")
            return []

    @classmethod
    def set_default_llm_model_cls(cls, model: str) -> None:
        """
        设置默认 LLM 模型（类方法）

        Usage: ToolsManager.set_default_llm_model_cls("gpt-4")

        Args:
            model: LLM 模型名称
        """
        cls._default_llm_model = model
        cls.clear_cache_cls()
        logger.info(f"Set default LLM model to: {model}")

    @classmethod
    def get_default_llm_model_cls(cls) -> str:
        """
        获取默认 LLM 模型（类方法）

        Usage: model = ToolsManager.get_default_llm_model_cls()

        Returns:
            默认 LLM 模型名称
        """
        return cls._default_llm_model

    @classmethod
    def clear_cache_cls(cls) -> None:
        """
        清除全局工具缓存（类方法）

        Usage: ToolsManager.clear_cache_cls()
        """
        cls._global_tools_cache = {}
        logger.info("Cleared global tools cache")

    @classmethod
    async def get_all_tools_cls(
            cls,
            db: Optional[Any] = None,
            mcp_manager: Optional[Any] = None
    ) -> Dict[str, List[Union[BaseTool, Callable[..., Any]]]]:
        """
        获取所有工具（类方法，无需初始化）- 包含本地工具和 MCP 工具

        Usage: tools = await ToolsManager.get_all_tools_cls(db, mcp_manager)

        Args:
            db: 数据库连接对象
            mcp_manager: 可选的 MCPManager 实例，用于获取 MCP 工具

        Returns:
            包含所有工具的字典，格式为:
            {
                "sql_tools": [SQL 数据库工具列表],
                "mcp_tools": {
                    "server_name": [工具列表],
                    ...
                },
                "all_tools": [所有工具的合并列表]
            }
        """
        result = {
            "sql_tools": [],
            "mcp_tools": {},
            "all_tools": [],
        }

        try:
            # 获取本地工具
            if db is not None:
                sql_tools = cls.get_sql_database_tools_cls(db)
                result["sql_tools"] = sql_tools
                result["all_tools"].extend(sql_tools)
                logger.info(f"Loaded {len(sql_tools)} local tools")

            # 获取 MCP 工具
            if mcp_manager is not None:
                try:
                    mcp_tools = await mcp_manager.get_all_tools()
                    result["mcp_tools"]["all"] = mcp_tools
                    result["all_tools"].extend(mcp_tools)
                    logger.info(f"Loaded {len(mcp_tools)} MCP tools")
                except Exception as e:
                    logger.warning(f"Failed to load MCP tools: {str(e)}")

            logger.info(f"Total loaded {len(result['all_tools'])} tools")
            return result
        except Exception as e:
            logger.error(f"Failed to get all tools: {str(e)}")
            return result


# ==================== 全局管理器实例 ====================

_tools_manager: Optional[ToolsManager] = None


def get_tools_manager(llm_model: Optional[str] = None) -> ToolsManager:
    """
    获取或创建全局工具管理器实例

    Args:
        llm_model: 可选的 LLM 模型名称

    Returns:
        ToolsManager 实例
    """
    global _tools_manager
    if _tools_manager is None:
        _tools_manager = ToolsManager(llm_model)
    return _tools_manager


# ==================== 向后兼容函数接口 ====================


def get_engine_for_chinook_db():
    """Pull sql file, populate in-memory database, and create engine."""
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    response = requests.get(url)
    sql_script = response.text

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

def get_sql_database_tools(db: Any) -> List[BaseTool]:
    """
    获取 SQL 数据库工具（向后兼容函数接口）

    Deprecated: 使用 ToolsManager.get_sql_database_tools_cls() 代替

    Args:
        db: 数据库连接对象

    Returns:
        SQL 数据库工具列表
    """
    return ToolsManager.get_sql_database_tools_cls(db)


def set_default_llm_model(model: str) -> None:
    """
    设置默认 LLM 模型（向后兼容函数接口）

    Deprecated: 使用 ToolsManager.set_default_llm_model_cls() 代替

    Args:
        model: LLM 模型名称
    """
    ToolsManager.set_default_llm_model_cls(model)


def get_default_llm_model() -> str:
    """
    获取默认 LLM 模型（向后兼容函数接口）

    Deprecated: 使用 ToolsManager.get_default_llm_model_cls() 代替

    Returns:
        默认 LLM 模型名称
    """
    return ToolsManager.get_default_llm_model_cls()


def clear_tools_cache() -> None:
    """
    清除工具缓存（向后兼容函数接口）

    Deprecated: 使用 ToolsManager.clear_cache_cls() 代替
    """
    ToolsManager.clear_cache_cls()


async def get_all_tools(
    db: Any, mcp_manager: Optional[Any] = None
) -> Dict[str, List[Union[BaseTool, Callable[..., Any]]]]:
    """
    获取所有工具（向后兼容函数接口）- 包含本地工具和 MCP 工具

    Deprecated: 使用 ToolsManager.get_all_tools_cls() 代替

    Args:
        db: 数据库连接对象
        mcp_manager: 可选的 MCPManager 实例，用于获取 MCP 工具

    Returns:
        包含所有工具的字典
    """
    return await ToolsManager.get_all_tools_cls(db, mcp_manager)
