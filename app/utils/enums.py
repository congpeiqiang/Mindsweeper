# 枚举类型定义

from enum import Enum


class FileStatus(str, Enum):
    """文件处理状态"""
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


class KBStatus(str, Enum):
    """知识库状态"""
    ACTIVE = "active"          # 活跃
    ARCHIVED = "archived"      # 已归档
    DELETED = "deleted"        # 已删除


class OperationType(str, Enum):
    """操作类型"""
    UPLOAD = "upload"          # 上传
    DELETE = "delete"          # 删除
    SEARCH = "search"          # 搜索
    UPDATE = "update"          # 更新
    CREATE = "create"          # 创建
    DOWNLOAD = "download"      # 下载


class ResourceType(str, Enum):
    """资源类型"""
    FILE = "file"              # 文件
    DOCUMENT = "document"      # 文档
    KNOWLEDGE_BASE = "knowledge_base"  # 知识库
    USER = "user"              # 用户


class OperationStatus(str, Enum):
    """操作状态"""
    SUCCESS = "success"        # 成功
    FAILED = "failed"          # 失败


class SortOrder(str, Enum):
    """排序顺序"""
    ASC = "asc"                # 升序
    DESC = "desc"              # 降序
