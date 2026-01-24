#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/1 16:34
# @Author  : CongPeiQiang
# @File    : test_inspector.py
# @Software: PyCharm

from sqlalchemy import create_engine, inspect

host="47.120.44.223"
username="postgres"
encoded_password="StrongPassword!"
port="5432"
database_name="myapp_db"

conn_str = (
                f"postgresql://{username}:"
                f"{encoded_password}@"
                f"{host}:{port}/{database_name}"
            )
engine = create_engine(conn_str)

inspector = inspect(engine)
# 返回tables表名列表
tables = inspector.get_table_names()
"""
['classes', 'students', 'grades', 'courses', 'teachers', 'class_teacher']
"""
print(tables)
# 返回views试图列表
views = inspector.get_view_names()
"""
['student_grades_view', 'class_info_view', 'teacher_info_view']
"""
print(views)
tables.extend(views)
for table_name in tables:
    print(f"===================={table_name}======================")
    # 主键信息
    pk_info = inspector.get_pk_constraint(table_name)
    print(pk_info)
    '''
    {'constrained_columns': ['class_id'], 'name': 'classes_pkey', 'comment': None, 'dialect_options': {'postgresql_include': []}}
    '''
    print(f"  主键约束名: {pk_info['name']}")
    print(f"  主键列名表: {pk_info['constrained_columns']}")
    if 'comment' in pk_info:
        print(f"  注释(描述): {pk_info['comment']}")
    '''
    主键约束名: classes_pkey
    主键列: ['class_id']
    注释(描述): None
    '''

    # 外键信息
    fks_infos = inspector.get_foreign_keys(table_name)
    print(fks_infos)
    """
    [{'comment': None, 'constrained_columns': ['class_id'], 'name': 'students_class_id_fkey', 'referred_columns': ['class_id'], 'referred_schema': None, 'referred_table': 'classes', 'options': {'ondelete': 'SET NULL'}, }]
    """
    if len(fks_infos) > 0:
        for fks_info in fks_infos:
            print(f"  外键约束名: {fks_info['name']}")
            print(f"  外键列名表: {fks_info['constrained_columns']}") # 如 ['course_id']
            print(f"  注释(描述): {fks_info['comment']}")
            print(f"  引用表所在的模式: {fks_info['referred_schema']}")
            print(f"  被引用的主表名: {fks_info['referred_table']}")
            print(f"  被引用的主表列名列表: {fks_info['referred_columns']}")
    '''
    外键约束名: students_class_id_fkey
    外键列: ['class_id']
    注释(描述): None
    '''

    indexes = inspector.get_indexes(table_name)
    print(f"  索引: {indexes}")

    # 属性信息
    columns = inspector.get_columns(table_name)
    for i, col in enumerate(columns, 1):
        print(f"\n列 {i}: {col['name']}")
        print(f"  数据类型: {col['type']}")
        print(f"  可空: {col['nullable']}")
        print(f"  默认值: {col['default']}")
        print(f"  自增: {col.get('autoincrement', False)}")  # 使用get避免KeyError
        print(f"  主键: {col.get('primary_key', False)}")
        print(f"  注释(描述): {col.get('comment', '无')}")
    '''
    列 1: class_id
        数据类型: INTEGER
        可空: False
        默认值: nextval('classes_class_id_seq'::regclass)
        自增: True
        主键: False
        注释(描述): None
    '''

    # """
    # columns:
    # {'autoincrement': True, 'comment': None, 'default': "nextval('classes_class_id_seq'::regclass)", 'name': 'class_id', 'nullable': False, 'type': INTEGER()}
    # """
    # print("***table_name columns***")
    # print(columns)
    #
    # pks = inspector.get_pk_constraint(table_name)
    # """
    # pks:
    # {'comment': None, 'constrained_columns': ['class_id'], 'dialect_options': {'postgresql_include': []}, 'name': 'classes_pkey'}
    # """
    # print("***table_name pks***")
    # print(pks)
    #
    # fks = inspector.get_foreign_keys(table_name)
    # """
    # fks:
    # [{'comment': None, 'constrained_columns': ['class_id'], 'name': 'students_class_id_fkey', 'options': {'ondelete': 'SET NULL'}, 'referred_columns': ['class_id'], 'referred_schema': None, 'referred_table': 'classes'}]
    # """
    # print("***table_name fks***")
    # print(fks)
    #
    # indexes = inspector.get_indexes(table_name)
    # print("***table_name indexes***")
    # print(indexes)
    # print("==========================================")
