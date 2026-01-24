# _*_ coding:utf-8_*_
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
from bson import ObjectId


class SingleDocumentCRUD:
    """单个文档的CRUD操作"""

    def __init__(self, db_name="test_db", collection_name="users"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # 确保集合有索引
        self.setup_indexes()

    def setup_indexes(self):
        """设置索引"""
        # 创建唯一索引
        self.collection.create_index("email", unique=True)
        self.collection.create_index("username", unique=True)

    def insert_single_document(self):
        """创建单个文档 - CREATE"""
        print("=== 创建单个文档 ===")

        user_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "age": 30,
            "city": "New York",
            "status": "active",
            "created_at": datetime.now(), # 需要自己设置created_at和updated_at
            "updated_at": datetime.now(),
            "tags": ["developer", "python", "mongodb"],
            "profile": {
                "bio": "Python developer",
                "website": "https://johndoe.com",
                "github": "johndoe"
            }
        }

        try:
            # 插入单个文档，返回的result包含inserted_id属性,inserted_id是Object对象
            result = self.collection.insert_one(user_data)
            print(f"✅ 文档创建成功!")
            print(f"   文档ID: {result.inserted_id}")
            print(f"   用户名: {user_data['username']}")
            print(f"   邮箱: {user_data['email']}")

            return result.inserted_id

        except DuplicateKeyError as e:
            print(f"❌ 创建失败: 用户名或邮箱已存在")
            return None
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return None

    def find_single_document(self, document_id=None, email=None):
        """读取单个文档 - READ"""
        print("\n=== 读取单个文档 ===")

        try:
            query = {}
            if document_id and isinstance(document_id, str):
                query["_id"] = ObjectId(document_id) # 如果_id是字符串，需要转换为ObjectId
            elif email:
                query["email"] = email
            else:
                # 随机读取一个文档
                document = self.collection.find_one()
                if document:
                    print("随机读取一个文档:")
                    self._print_document(document)
                return document

            # 根据查询条件读取
            document = self.collection.find_one(query)

            if document:
                print(f"找到文档:")
                self._print_document(document)
            else:
                print("未找到匹配的文档")

            return document

        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return None

    def update_single_document(self, document_id):
        """更新单个文档 - UPDATE"""
        print("\n=== 更新单个文档 ===")

        if not document_id:
            print("需要提供文档ID")
            return None

        try:
            # 更新操作1: 设置字段值
            update_result1 = self.collection.update_one(
                {"_id": document_id},
                {
                    "$set": {
                        "age": 31,
                        "city": "San Francisco",
                        "updated_at": datetime.now(),
                        "profile.bio": "Senior Python Developer at Tech Corp"
                    }
                }
            )

            print(f"1. 基础更新:")
            print(f"   匹配文档数: {update_result1.matched_count}")
            print(f"   修改文档数: {update_result1.modified_count}")

            # 更新操作2: 增加数值
            update_result2 = self.collection.update_one(
                {"_id": document_id},
                {
                    "$inc": {"age": 1}  # 年龄加1
                }
            )
            print(f"2. 数值增加:")
            print(f"   修改后年龄增加1岁")

            # 更新操作3: 添加元素到数组
            update_result3 = self.collection.update_one(
                {"_id": document_id},
                {
                    "$push": {"tags": "backend"}
                }
            )
            print(f"3. 添加数组元素:")
            print(f"   添加 'backend' 到标签")

            # 更新操作4: 删除字段
            update_result4 = self.collection.update_one(
                {"_id": document_id},
                {
                    "$unset": {"status": ""}
                }
            )
            print(f"4. 删除字段:")
            print(f"   删除 status 字段")

            # 更新操作5: 重命名字段
            update_result5 = self.collection.update_one(
                {"_id": document_id},
                {
                    "$rename": {"full_name": "name"}
                }
            )
            print(f"5. 重命名字段:")
            print(f"   full_name 重命名为 name")

            # 显示更新后的文档
            updated_doc = self.collection.find_one({"_id": document_id})
            print(f"\n更新后的文档:")
            self._print_document(updated_doc)

            return update_result1.modified_count > 0

        except Exception as e:
            print(f"❌ 更新失败: {e}")
            return False

    def replace_single_document(self, document_id):
        """替换整个文档"""
        print("\n=== 替换整个文档 ===")

        new_document = {
            "username": "john_doe_updated",
            "email": "john.updated@example.com",
            "name": "John Doe Jr.",
            "age": 32,
            "profession": "Software Engineer",
            "skills": ["Python", "MongoDB", "FastAPI", "Docker"],
            "updated_time":datetime.now(),
            "experience_years": 8,
            "last_updated": datetime.now(),
            "metadata": {
                "version": 2,
                "update_reason": "Complete profile overhaul"
            }
        }

        try:
            # 注意: replace_one 会替换整个文档，只保留_id,返回的result包含matched_count和modified_count属性
            result = self.collection.replace_one(
                {"_id": document_id},
                new_document
            )

            print(f"文档替换结果:")
            print(f"   匹配文档数: {result.matched_count}")
            print(f"   修改文档数: {result.modified_count}")

            if result.modified_count > 0:
                replaced_doc = self.collection.find_one({"_id": document_id})
                print(f"\n替换后的文档:")
                self._print_document(replaced_doc)

            return result.modified_count > 0

        except Exception as e:
            print(f"❌ 替换失败: {e}")
            return False

    def delete_single_document(self, document_id):
        """删除单个文档 - DELETE"""
        print("\n=== 删除单个文档 ===")

        try:
            # 先显示要删除的文档
            document_to_delete = self.collection.find_one({"_id": document_id})
            if not document_to_delete:
                print("文档不存在")
                return False

            print("要删除的文档:")
            self._print_document(document_to_delete)

            # 确认删除
            confirm = input("\n确认删除此文档? (y/N): ")
            if confirm.lower() != 'y':
                print("取消删除")
                return False

            # 执行删除
            result = self.collection.delete_one({"_id": document_id})

            if result.deleted_count > 0:
                print(f"✅ 文档删除成功!")
                print(f"   删除文档数: {result.deleted_count}")
                return True
            else:
                print("文档删除失败")
                return False

        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False

    def upsert_single_document(self, username):
        """更新或插入文档（upsert）"""
        print("\n=== 更新或插入文档 ===")

        user_data = {
            "username": username,
            "email": f"{username}@example.com",
            "name": f"{username.capitalize()} User",
            "last_login": datetime.now(),
            "login_count": 1
        }

        try:
            # 使用 upsert: 如果存在则更新，不存在则插入
            result = self.collection.update_one(
                {"username": username},
                {
                    "$set": {"last_login": datetime.now()},
                    "$inc": {"login_count": 1},
                    "$setOnInsert": user_data  # 只在插入时设置这些字段
                },
                upsert=True  # 关键参数
            )

            if result.upserted_id:
                print(f"✅ 插入新文档!")
                print(f"   新文档ID: {result.upserted_id}")
                print(f"   用户名: {username}")
            else:
                print(f"✅ 更新现有文档!")
                print(f"   匹配文档数: {result.matched_count}")
                print(f"   修改文档数: {result.modified_count}")

            return result.upserted_id or result.modified_count > 0

        except Exception as e:
            print(f"❌ Upsert失败: {e}")
            return False

    def _print_document(self, document):
        """打印文档内容"""
        if not document:
            print("文档为空")
            return

        print("-" * 40)
        for key, value in document.items():
            if key == "_id":
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"  {key}: {', '.join(map(str, value))}")
            else:
                print(f"  {key}: {value}")
        print("-" * 40)

    def run_all_operations(self):
        """运行所有单个文档操作"""
        print("=" * 60)
        print("单个文档CRUD操作演示")
        print("=" * 60)

        try:
            # 1. 创建文档
            doc_id = self.insert_single_document()

            if doc_id:
                # 2. 读取文档
                self.find_single_document(document_id=str(doc_id))

                # 3. 更新文档
                self.update_single_document(doc_id)

                # 4. 再次读取验证更新
                self.find_single_document(document_id=doc_id)

                # 5. 替换文档，根据_id字段替换整个document
                self.replace_single_document(doc_id)

                # 6. Upsert操作
                self.upsert_single_document("jane_smith")
                self.upsert_single_document("jane_smith")  # 第二次会更新

                # 7. 删除文档
                self.delete_single_document(doc_id)

                # 8. 验证删除
                self.find_single_document(document_id=doc_id)

        finally:
            self.client.close()


# 运行单个文档示例
if __name__ == "__main__":
    single_crud = SingleDocumentCRUD()
    single_crud.run_all_operations()