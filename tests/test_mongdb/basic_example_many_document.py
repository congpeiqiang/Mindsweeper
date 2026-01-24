# _*_ coding:utf-8_*_
from pymongo import MongoClient
from datetime import datetime, timedelta
import random


class MultipleDocumentsCRUD:
    """多个文档的CRUD操作"""

    def __init__(self, db_name="test_db", collection_name="products"):
        self.client = MongoClient("mongodb://47.120.44.223:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_multiple_documents(self):
        """创建多个文档 - CREATE"""
        print("=" * 60)
        print("创建多个文档")
        print("=" * 60)

        # 示例1: 基础批量插入
        print("\n1. 基础批量插入")
        products = [
            {
                "name": "Laptop Pro",
                "category": "Electronics",
                "price": 1299.99,
                "stock": 50,
                "tags": ["computer", "laptop", "tech"],
                "created_at": datetime.now()
            },
            {
                "name": "Wireless Mouse",
                "category": "Electronics",
                "price": 39.99,
                "stock": 200,
                "tags": ["computer", "accessory"],
                "created_at": datetime.now()
            },
            {
                "name": "Desk Chair",
                "category": "Furniture",
                "price": 299.99,
                "stock": 30,
                "tags": ["office", "furniture"],
                "created_at": datetime.now()
            },
            {
                "name": "Coffee Mug",
                "category": "Home",
                "price": 15.99,
                "stock": 150,
                "tags": ["kitchen", "home"],
                "created_at": datetime.now()
            }
        ]

        result = self.collection.insert_many(products)
        print(f"✅ 批量插入 {len(result.inserted_ids)} 个文档")
        print(f"   插入的ID: {result.inserted_ids[:3]}...")  # 只显示前3个

        # 示例2: 生成大量测试数据
        print("\n2. 生成大量测试数据")
        bulk_data = []
        categories = ["Electronics", "Clothing", "Books", "Sports", "Food"]
        statuses = ["active", "inactive", "pending", "discontinued"]

        for i in range(1, 101):  # 生成100个文档
            category = random.choice(categories)
            price = round(random.uniform(10, 1000), 2)

            product = {
                "product_id": f"PROD{i:04d}",
                "name": f"Product {i}",
                "category": category,
                "price": price,
                "discount_price": round(price * random.uniform(0.7, 0.9), 2),
                "stock": random.randint(0, 500),
                "rating": round(random.uniform(1, 5), 1),
                "status": random.choice(statuses),
                "created_date": datetime.now() - timedelta(days=random.randint(0, 365)),
                "features": [f"feature_{j}" for j in range(1, random.randint(2, 6))],
                "metadata": {
                    "supplier": f"Supplier {random.randint(1, 10)}",
                    "weight": f"{random.randint(1, 10)}kg",
                    "dimensions": f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm"
                }
            }
            bulk_data.append(product)

        try:
            result = self.collection.insert_many(bulk_data)
            print(f"✅ 批量插入 {len(result.inserted_ids)} 个测试文档")
        except Exception as e:
            print(f"⚠️  部分文档可能已存在: {e}")

        return len(products) + len(bulk_data)

    def find_multiple_documents(self):
        """读取多个文档 - READ"""
        print("\n" + "=" * 60)
        print("读取多个文档")
        print("=" * 60)

        # 示例1: 查询所有文档
        print("\n1. 查询所有文档（限制显示5个）")
        all_docs = self.collection.find().limit(5)
        count = self.collection.count_documents({})
        print(f"   总文档数: {count}")
        print(f"   前5个文档:")
        for i, doc in enumerate(all_docs, 1):
            print(f"   {i}. {doc.get('name', 'N/A')} - ${doc.get('price', 0)}")

        # 示例2: 条件查询
        print("\n2. 条件查询: 电子类产品")
        electronics = self.collection.find(
            {"category": "Electronics"}
        ).limit(5)

        electronics_count = self.collection.count_documents({"category": "Electronics"})
        print(f"   电子类产品数量: {electronics_count}")
        for doc in electronics:
            print(f"   - {doc.get('name')}: ${doc.get('price')}")

        # 示例3: 范围查询
        print("\n3. 范围查询: 价格在 $50-$200 之间的产品")
        price_range_docs = self.collection.find(
            {"price": {"$gte": 50, "$lte": 200}}
        ).limit(5)

        for doc in price_range_docs:
            print(f"   - {doc.get('name')}: ${doc.get('price')}")

        # 示例4: 复杂查询
        print("\n4. 复杂查询: 库存>100且评分>4.0的活跃产品")
        complex_query = {
            "stock": {"$gt": 100},
            "rating": {"$gt": 4.0},
            "status": "active"
        }

        complex_docs = self.collection.find(complex_query).limit(5)
        for doc in complex_docs:
            print(f"   - {doc.get('name')}: 评分{doc.get('rating')}, 库存{doc.get('stock')}")

        # 示例5: 数组查询
        print("\n5. 数组查询: 包含特定标签的产品")
        array_query = self.collection.find(
            {"tags": {"$in": ["computer", "tech"]}}
        ).limit(5)

        for doc in array_query:
            print(f"   - {doc.get('name')}: 标签 {doc.get('tags', [])}")

        # 示例6: 排序和分页
        print("\n6. 排序和分页: 按价格降序，第2页")
        sorted_docs = self.collection.find(
            {},
            {"name": 1, "price": 1, "_id": 0}
        ).sort("price", -1).skip(10).limit(5)  # 第2页，每页10个

        print("   价格最高的产品（第2页）:")
        for doc in sorted_docs:
            print(f"   - {doc.get('name')}: ${doc.get('price')}")

        # 示例7: 使用投影
        print("\n7. 使用投影: 只返回指定字段")
        projected_docs = self.collection.find(
            {"category": "Electronics"},
            {"name": 1, "price": 1, "stock": 1, "_id": 0}
        ).limit(3)

        for doc in projected_docs:
            print(f"   - {doc}")

    def update_multiple_documents(self):
        """更新多个文档 - UPDATE"""
        print("\n" + "=" * 60)
        print("更新多个文档")
        print("=" * 60)

        # 示例1: 更新所有文档
        print("\n1. 更新所有文档: 添加更新时间")
        result1 = self.collection.update_many(
            {},  # 空查询条件匹配所有文档
            {
                "$set": {"last_updated": datetime.now()},
                "$currentDate": {"modified_at": True}
            }
        )
        print(f"   匹配文档数: {result1.matched_count}")
        print(f"   修改文档数: {result1.modified_count}")

        # 示例2: 条件更新多个文档
        print("\n2. 条件更新: 为电子类产品添加折扣")
        result2 = self.collection.update_many(
            {"category": "Electronics"},
            {
                "$set": {"has_discount": True},
                "$mul": {"discount_price": 0.9}  # 打9折
            }
        )
        print(f"   匹配电子类产品数: {result2.matched_count}")
        print(f"   修改电子类产品数: {result2.modified_count}")

        # 示例3: 增加库存
        print("\n3. 数值操作: 所有产品库存增加10%")
        result3 = self.collection.update_many(
            {},
            {
                "$mul": {"stock": 1.1},  # 增加10%
                "$inc": {"version": 1}  # 版本号加1
            }
        )
        print(f"   更新库存的产品数: {result3.modified_count}")

        # 示例4: 数组操作
        print("\n4. 数组操作: 为特定产品添加标签")
        result4 = self.collection.update_many(
            {"category": "Electronics", "price": {"$gt": 100}},
            {
                "$addToSet": {"tags": "premium"}  # 避免重复添加
            }
        )
        print(f"   添加'tag'标签的产品数: {result4.modified_count}")

        # 示例5: 删除字段
        print("\n5. 删除字段: 移除状态为'discontinued'的产品的某些字段")
        result5 = self.collection.update_many(
            {"status": "discontinued"},
            {
                "$unset": {
                    "discount_price": "",
                    "has_discount": ""
                }
            }
        )
        print(f"   清理字段的产品数: {result5.modified_count}")

        # 示例6: 批量替换（使用bulk write）
        print("\n6. 批量替换操作")

        # 获取一些要替换的文档
        products_to_replace = list(self.collection.find(
            {"category": "Clothing"}
        ).limit(3))

        operations = []
        for product in products_to_replace:
            new_product = {
                "name": f"Updated {product['name']}",
                "category": product["category"],
                "price": product["price"] * 0.8,  # 20%折扣
                "stock": product["stock"] + 50,
                "is_updated": True,
                "update_date": datetime.now()
            }
            operations.append(
                UpdateOne(
                    {"_id": product["_id"]},
                    {"$set": new_product}
                )
            )

        if operations:
            bulk_result = self.collection.bulk_write(operations)
            print(f"   批量替换操作数: {bulk_result.modified_count}")

    def delete_multiple_documents(self):
        """删除多个文档 - DELETE"""
        print("\n" + "=" * 60)
        print("删除多个文档")
        print("=" * 60)

        # 显示当前文档数
        initial_count = self.collection.count_documents({})
        print(f"   当前文档总数: {initial_count}")

        # 示例1: 删除所有测试数据（谨慎使用！）
        print("\n1. 删除所有测试产品")
        confirm = input("   确认删除所有测试数据? (输入'DELETE'确认): ")

        if confirm == "DELETE":
            result1 = self.collection.delete_many({
                "product_id": {"$regex": "^PROD"}
            })
            print(f"   删除测试产品数: {result1.deleted_count}")
        else:
            print("   取消删除测试数据")

        # 示例2: 条件删除
        print("\n2. 条件删除: 删除库存为0的产品")
        result2 = self.collection.delete_many({"stock": 0})
        print(f"   删除零库存产品数: {result2.deleted_count}")

        # 示例3: 删除过期或无效数据
        print("\n3. 删除状态为'discontinued'且库存<10的产品")
        result3 = self.collection.delete_many({
            "status": "discontinued",
            "stock": {"$lt": 10}
        })
        print(f"   删除废弃产品数: {result3.deleted_count}")

        # 示例4: 删除特定类别的所有文档
        print("\n4. 删除特定类别: 删除'Test'类别的所有产品")
        result4 = self.collection.delete_many({"category": "Test"})
        print(f"   删除测试类别产品数: {result4.deleted_count}")

        # 显示最终文档数
        final_count = self.collection.count_documents({})
        print(f"\n   最终文档总数: {final_count}")
        print(f"   总共删除文档数: {initial_count - final_count}")

    def bulk_operations_example(self):
        """批量操作示例"""
        print("\n" + "=" * 60)
        print("批量操作（混合增删改）")
        print("=" * 60)

        from pymongo import InsertOne, UpdateOne, DeleteOne

        # 创建批量操作列表
        operations = []

        # 插入操作
        operations.append(InsertOne({
            "name": "Bulk Product 1",
            "category": "Bulk",
            "price": 99.99,
            "batch": 1
        }))

        operations.append(InsertOne({
            "name": "Bulk Product 2",
            "category": "Bulk",
            "price": 149.99,
            "batch": 1
        }))

        # 更新操作
        operations.append(UpdateOne(
            {"category": "Electronics", "price": {"$lt": 50}},
            {"$set": {"price_tier": "budget"}}
        ))

        # 删除操作
        operations.append(DeleteOne(
            {"name": "Coffee Mug"}
        ))

        # 执行批量操作
        try:
            result = self.collection.bulk_write(operations)

            print(f"批量操作结果:")
            print(f"   插入文档数: {result.inserted_count}")
            print(f"   更新文档数: {result.modified_count}")
            print(f"   删除文档数: {result.deleted_count}")
            print(f"   匹配但未更新: {result.upserted_count}")
            print(f"   批量操作ID: {result.bulk_api_result}")

        except Exception as e:
            print(f"批量操作失败: {e}")

    def find_and_modify_example(self):
        """查找并修改示例"""
        print("\n" + "=" * 60)
        print("查找并修改操作")
        print("=" * 60)

        # 示例1: find_one_and_update
        print("\n1. find_one_and_update: 更新并返回旧文档")
        old_doc = self.collection.find_one_and_update(
            {"category": "Electronics", "stock": {"$gt": 0}},
            {"$inc": {"stock": -1}},  # 库存减1
            return_document=False  # 返回更新前的文档
        )
        print(f"   更新的产品: {old_doc.get('name') if old_doc else '无'}")
        print(f"   原库存: {old_doc.get('stock') if old_doc else '无'}")

        # 示例2: find_one_and_replace
        print("\n2. find_one_and_replace: 替换并返回新文档")
        new_doc = {
            "name": "Replaced Product",
            "category": "Special",
            "price": 999.99,
            "replacement_date": datetime.now()
        }

        replaced_doc = self.collection.find_one_and_replace(
            {"category": "Furniture"},
            new_doc,
            return_document=True  # 返回替换后的文档
        )
        print(f"   替换后的文档: {replaced_doc.get('name') if replaced_doc else '无'}")

        # 示例3: find_one_and_delete
        print("\n3. find_one_and_delete: 删除并返回被删除的文档")
        deleted_doc = self.collection.find_one_and_delete(
            {"category": "Home"}
        )
        print(f"   删除的文档: {deleted_doc.get('name') if deleted_doc else '无'}")

    def run_all_operations(self):
        """运行所有多个文档操作"""
        try:
            # 创建数据
            self.insert_multiple_documents()

            # 读取数据
            self.find_multiple_documents()

            # 更新数据
            self.update_multiple_documents()

            # 批量操作
            self.bulk_operations_example()

            # 查找并修改
            self.find_and_modify_example()

            # 最后删除数据（可选）
            # self.delete_multiple_documents()

        finally:
            # 清理测试集合（可选）
            # self.collection.drop()
            self.client.close()


# 运行多个文档示例
if __name__ == "__main__":
    # 需要导入 UpdateOne
    from pymongo import UpdateOne

    multi_crud = MultipleDocumentsCRUD()
    multi_crud.run_all_operations()