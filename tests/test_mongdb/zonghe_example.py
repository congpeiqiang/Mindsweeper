# _*_ coding:utf-8_*_
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional


class StudentManagementSystem:
    """学生管理系统 - 综合CRUD示例"""

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["school_management"]
        self.students = self.db["students"]
        self.courses = self.db["courses"]

        # 初始化数据
        self._initialize_data()

    def _initialize_data(self):
        """初始化测试数据"""
        # 初始化课程
        if self.courses.count_documents({}) == 0:
            courses_data = [
                {"course_code": "CS101", "name": "计算机基础", "credits": 3},
                {"course_code": "CS102", "name": "数据结构", "credits": 4},
                {"course_code": "MATH101", "name": "高等数学", "credits": 4},
                {"course_code": "ENG101", "name": "大学英语", "credits": 2}
            ]
            self.courses.insert_many(courses_data)

    def add_student_single(self):
        """添加单个学生"""
        print("=== 添加单个学生 ===")

        student = {
            "student_id": "S2024001",
            "name": "张三",
            "age": 20,
            "gender": "男",
            "major": "计算机科学",
            "enrollment_date": datetime.now(),
            "courses_enrolled": ["CS101", "MATH101"],
            "gpa": 3.5,
            "contact": {
                "email": "zhangsan@school.com",
                "phone": "13800138000",
                "address": "北京市海淀区"
            },
            "status": "active"
        }

        try:
            result = self.students.insert_one(student)
            print(f"✅ 学生添加成功!")
            print(f"   学号: {student['student_id']}")
            print(f"   姓名: {student['name']}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ 添加失败: {e}")
            return None

    def add_students_batch(self):
        """批量添加学生"""
        print("\n=== 批量添加学生 ===")

        students = [
            {
                "student_id": "S2024002",
                "name": "李四",
                "age": 21,
                "major": "软件工程",
                "gpa": 3.8,
                "status": "active"
            },
            {
                "student_id": "S2024003",
                "name": "王五",
                "age": 22,
                "major": "计算机科学",
                "gpa": 3.2,
                "status": "active"
            },
            {
                "student_id": "S2024004",
                "name": "赵六",
                "age": 19,
                "major": "数学",
                "gpa": 3.9,
                "status": "active"
            }
        ]

        try:
            result = self.students.insert_many(students)
            print(f"✅ 批量添加 {len(result.inserted_ids)} 名学生")
            return result.inserted_ids
        except Exception as e:
            print(f"❌ 批量添加失败: {e}")
            return []

    def query_students(self):
        """查询学生"""
        print("\n" + "=" * 60)
        print("查询学生")
        print("=" * 60)

        # 查询所有学生
        print("\n1. 所有学生:")
        all_students = list(self.students.find({}, {"name": 1, "major": 1, "gpa": 1, "_id": 0}))
        for student in all_students:
            print(f"   {student.get('name')} - {student.get('major')} - GPA: {student.get('gpa')}")

        # 条件查询
        print("\n2. 计算机科学专业的学生:")
        cs_students = self.students.find(
            {"major": "计算机科学"},
            {"name": 1, "gpa": 1, "_id": 0}
        )
        for student in cs_students:
            print(f"   {student.get('name')} - GPA: {student.get('gpa')}")

        # 范围查询
        print("\n3. GPA大于3.5的学生:")
        high_gpa_students = self.students.find(
            {"gpa": {"$gt": 3.5}},
            {"name": 1, "gpa": 1, "major": 1, "_id": 0}
        ).sort("gpa", -1)  # 按GPA降序

        for student in high_gpa_students:
            print(f"   {student.get('name')} - {student.get('major')} - GPA: {student.get('gpa')}")

    def update_student_single(self, student_id):
        """更新单个学生"""
        print(f"\n=== 更新单个学生 {student_id} ===")

        updates = {
            "$set": {
                "gpa": 3.7,
                "updated_at": datetime.now(),
                "contact.email": "updated.email@school.com"
            },
            "$inc": {"age": 1},  # 年龄加1
            "$addToSet": {"courses_enrolled": "CS102"}  # 添加课程
        }

        result = self.students.update_one(
            {"student_id": student_id},
            updates
        )

        if result.matched_count > 0:
            print(f"✅ 更新成功!")
            print(f"   匹配学生数: {result.matched_count}")
            print(f"   修改学生数: {result.modified_count}")
        else:
            print("未找到该学生")

    def update_students_batch(self):
        """批量更新学生"""
        print("\n=== 批量更新学生 ===")

        # 为所有GPA>3.5的学生添加荣誉标志
        result = self.students.update_many(
            {"gpa": {"$gt": 3.5}},
            {
                "$set": {"honors": True},
                "$currentDate": {"honors_date": True}
            }
        )

        print(f"✅ 批量更新成功!")
        print(f"   匹配学生数: {result.matched_count}")
        print(f"   修改学生数: {result.modified_count}")
        print(f"   现在有 {result.modified_count} 名学生获得荣誉")

    def delete_student_single(self, student_id):
        """删除单个学生"""
        print(f"\n=== 删除单个学生 {student_id} ===")

        result = self.students.delete_one({"student_id": student_id})

        if result.deleted_count > 0:
            print(f"✅ 删除成功!")
            print(f"   删除学生数: {result.deleted_count}")
        else:
            print("未找到该学生")

    def delete_students_batch(self):
        """批量删除学生"""
        print("\n=== 批量删除学生 ===")

        # 删除GPA低于2.0且状态为inactive的学生
        result = self.students.delete_many({
            "gpa": {"$lt": 2.0},
            "status": "inactive"
        })

        print(f"✅ 批量删除成功!")
        print(f"   删除学生数: {result.deleted_count}")

    def complex_operations(self):
        """复杂操作示例"""
        print("\n" + "=" * 60)
        print("复杂操作")
        print("=" * 60)

        # 事务示例（需要副本集）
        print("\n1. 事务操作（模拟）:")
        try:
            # 模拟事务操作
            student_updates = [
                {"$set": {"status": "graduated", "graduation_date": datetime.now()}}
            ]

            # 更新所有active状态的学生
            result = self.students.update_many(
                {"status": "active", "gpa": {"$gte": 2.0}},
                student_updates
            )
            print(f"   成功将 {result.modified_count} 名学生标记为毕业")

        except Exception as e:
            print(f"   事务失败: {e}")

        # 聚合查询
        print("\n2. 聚合查询 - 各专业统计:")
        pipeline = [
            {"$group": {
                "_id": "$major",
                "avg_gpa": {"$avg": "$gpa"},
                "student_count": {"$sum": 1},
                "max_gpa": {"$max": "$gpa"},
                "min_gpa": {"$min": "$gpa"}
            }},
            {"$sort": {"avg_gpa": -1}}
        ]

        major_stats = self.students.aggregate(pipeline)
        for stat in major_stats:
            print(f"   专业: {stat['_id']}")
            print(f"     学生数: {stat['student_count']}")
            print(f"     平均GPA: {stat['avg_gpa']:.2f}")
            print(f"     最高GPA: {stat['max_gpa']}")
            print(f"     最低GPA: {stat['min_gpa']}")

    def run_demo(self):
        """运行演示"""
        print("=" * 60)
        print("学生管理系统 - MongoDB CRUD综合演示")
        print("=" * 60)

        try:
            # 添加学生
            print("\n📝 添加学生:")
            student1_id = self.add_student_single()
            student_ids = self.add_students_batch()

            # 查询学生
            print("\n🔍 查询学生:")
            self.query_students()

            if student1_id:
                # 更新单个学生
                print("\n✏️  更新学生:")
                self.update_student_single("S2024001")

                # 批量更新
                self.update_students_batch()

                # 删除单个学生
                print("\n🗑️  删除学生:")
                self.delete_student_single("S2024004")

            # 批量删除（模拟）
            print("\n⚠️  批量删除:")
            self.delete_students_batch()

            # 复杂操作
            self.complex_operations()

            # 最终统计
            total_students = self.students.count_documents({})
            print(f"\n📊 最终统计: 系统中共有 {total_students} 名学生")

        finally:
            self.client.close()


# 运行综合示例
if __name__ == "__main__":
    sms = StudentManagementSystem()
    sms.run_demo()

"""
操作	单个文档方法	多个文档方法	说明
创建	insert_one()	insert_many()	单个插入返回InsertOneResult，批量插入返回InsertManyResult
读取	find_one()	find()	find_one返回单个文档或None，find返回游标
更新	update_one()	update_many()	都需要指定更新操作符($set, $inc等)
替换	replace_one()	无直接方法	可使用update_many配合$set实现批量替换
删除	delete_one()	delete_many()	根据查询条件删除文档
返回值	返回具体文档ID	返回多个文档ID	批量操作返回结果列表
性能	适合精确操作	适合批量处理	批量操作通常更高效
"""