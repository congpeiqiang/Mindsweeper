# _*_ coding:utf-8_*_
from typing import List, Union, Optional, Dict

from pymongo import InsertOne, UpdateOne, UpdateMany, DeleteOne, DeleteMany, ReplaceOne, MongoClient
from pymongo.errors import BulkWriteError, PyMongoError


def bulk_write(operations: List[Union[InsertOne, UpdateOne, UpdateMany, DeleteOne, DeleteMany, ReplaceOne]],
               ordered: bool = True) -> Optional[Dict]:
    """
    批量写操作（替代多个update_many）

    Args:
        operations: 批量操作列表
        ordered: 是否按顺序执行

    Returns:
        批量写结果统计

    Examples:
        # 使用示例
        operations = [
            InsertOne({"name": "张三", "age": 25}),
            # UpdateOne: 部分更新,只更新指定的字段，其他字段保持不变;使用 $set, $inc, $push 等操作符;保留文档的 _id 和其他未指定字段
            UpdateOne({"name": "李四"}, {"$set": {"age": 30}}),
            UpdateMany({"status": "active"}, {"$inc": {"score": 10}}),
            DeleteOne({"name": "王五"}),
            # ReplaceOne: 完全替换：用新文档替换整个文档（除了 _id）; 不保留原文档的任何字段（除非在新文档中明确指定）;相当于删除旧文档并插入新文档
            ReplaceOne({"name": "赵六"}, {"name": "赵六", "age": 35, "status": "vip"})
        ]

        result = manager.bulk_write("users", operations)
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["test_db"]
        collection = db["users1"]
        # 执行批量操作
        result = collection.bulk_write(operations, ordered=ordered)

        return {
            'inserted_count': result.inserted_count,
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'deleted_count': result.deleted_count,
            'upserted_count': result.upserted_count,
            'bulk_api_result': result.bulk_api_result if hasattr(result, 'bulk_api_result') else None
        }

    except BulkWriteError as e:
        # 批量操作部分失败的情况
        error_result = {
            'error': True,
            'error_details': str(e.details),
            'inserted_count': e.details.get('nInserted', 0),
            'matched_count': e.details.get('nMatched', 0),
            'modified_count': e.details.get('nModified', 0),
            'deleted_count': e.details.get('nRemoved', 0),
            'upserted_count': len(e.details.get('upserted', []))
        }
        print(f"批量操作部分失败: {e.details}")
        return error_result

    except PyMongoError as e:
        print(e)
        return None

operations = [
            # InsertOne({"name": "李五", "age": 66, "status": "active"}),
            # InsertOne({"name": "李五", "age": 27, "status": "active"}),
            # UpdateOne: 部分更新,只更新指定的字段，其他字段保持不变;使用 $set, $inc, $push 等操作符;保留文档的 _id 和其他未指定字段
            # UpdateOne({"name": "李五"}, {"$set": {"age": 30}}),
            # UpdateMany({"status": "active"}, {"$inc": {"score": 10}}),
            # DeleteOne({"name": "李五"}),
            # DeleteMany({"name": "李五"}),
            # ReplaceOne: 完全替换：用新文档替换整个文档（除了 _id）; 不保留原文档的任何字段（除非在新文档中明确指定）;相当于删除旧文档并插入新文档
            ReplaceOne({"name": "李七"}, {"name": "赵六", "age": 35, "status": "vip"})
        ]
bulk_write(operations=operations)