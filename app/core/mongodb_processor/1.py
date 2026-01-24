#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 15:03
# @Author  : CongPeiQiang
# @File    : 1.py
# @Software: PyCharm
class MongoDBConfig:
    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database


class MongoDBManagerFactory:
    @staticmethod
    def create_manager(config: MongoDBConfig, manager_name: str):
        # 这里应该是实际的 MongoDB 管理器创建逻辑
        # 暂时返回一个简单的模拟对象
        return type('MongoDBManager', (), {
            'name': manager_name,
            'config': config
        })()


class DocumentManager:
    def __init__(
            self,
            input_dir: str,
            workspace: str = "",  # New parameter for workspace isolation
            supported_extensions: tuple = (
                    ".txt",
                    ".md",
                    ".mdx",  # MDX (Markdown + JSX)
                    ".pdf",
                    ".docx",
                    ".pptx",
                    ".xlsx",
                    ".rtf",  # Rich Text Format
                    ".odt",  # OpenDocument Text
                    ".tex",  # LaTeX
                    ".epub",  # Electronic Publication
                    ".html",  # HyperText Markup Language
                    ".htm",  # HyperText Markup Language
                    ".csv",  # Comma-Separated Values
                    ".json",  # JavaScript Object Notation
                    ".xml",  # eXtensible Markup Language
                    ".yaml",  # YAML Ain't Markup Language
                    ".yml",  # YAML
                    ".log",  # Log files
                    ".conf",  # Configuration files
                    ".ini",  # Initialization files
                    ".properties",  # Java properties files
                    ".sql",  # SQL scripts
                    ".bat",  # Batch files
                    ".sh",  # Shell scripts
                    ".c",  # C source code
                    ".cpp",  # C++ source code
                    ".py",  # Python source code
                    ".java",  # Java source code
                    ".js",  # JavaScript source code
                    ".ts",  # TypeScript source code
                    ".swift",  # Swift source code
                    ".go",  # Go source code
                    ".rb",  # Ruby source code
                    ".php",  # PHP source code
                    ".css",  # Cascading Style Sheets
                    ".scss",  # Sassy CSS
                    ".less",  # LESS CSS
            ),
            config=None,  # 默认设为 None
            mongdb_manager=None  # 默认设为 None
    ):
        # 设置默认配置，如果未提供
        if config is None:
            config = MongoDBConfig(
                host="47.120.44.223",
                port=27017,
                database="test_db"
            )

        # 设置默认 MongoDB 管理器，如果未提供
        if mongdb_manager is None:
            mongdb_manager = MongoDBManagerFactory.create_manager(
                config=config,
                manager_name="test-2026-01-22"
            )

        self.input_dir = input_dir
        self.workspace = workspace
        self.supported_extensions = supported_extensions
        self.config = config
        self.mongdb_manager = mongdb_manager
