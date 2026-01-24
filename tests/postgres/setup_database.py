
import psycopg2
from psycopg2 import sql
import os

# 数据库连接参数
DB_PARAMS = {
    'host': '47.120.44.223',
    'port': 5432,
    'user': 'postgres',
    'password': 'StrongPassword!',
    'database': 'myapp_db'
}

def execute_sql_file(sql_file_path):
    """执行SQL文件"""
    try:
        # 连接到数据库
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True  # 自动提交事务
        cursor = conn.cursor()

        print(f"成功连接到数据库: {DB_PARAMS['host']}:{DB_PARAMS['port']}")

        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"正在执行SQL文件: {sql_file_path}")

        # 执行SQL语句
        cursor.execute(sql_content)

        print("SQL文件执行成功！")

        # 关闭连接
        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"执行SQL文件时出错: {e}")
        return False

def main():
    # 获取SQL文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, 'student_management_system.sql')

    # 检查SQL文件是否存在
    if not os.path.exists(sql_file_path):
        print(f"错误: 找不到SQL文件 {sql_file_path}")
        return

    # 执行SQL文件
    success = execute_sql_file(sql_file_path)

    if success:
        print("学生管理系统数据库设置完成！")
    else:
        print("学生管理系统数据库设置失败！")

if __name__ == "__main__":
    main()
