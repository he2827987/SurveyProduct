#!/usr/bin/env python3
"""
数据迁移脚本：从MySQL导出数据并导入到PostgreSQL
使用方法：python migrate_data.py
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
import psycopg2
from psycopg2.extras import RealDictCursor

# 数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # 请填入MySQL密码
    'database': 'survey_db',
    'charset': 'utf8mb4'
}

POSTGRES_CONFIG = {
    'host': 'dpg-d6e354npm1nc73a62u9g-a.oregon-postgres.render.com',
    'port': 5432,
    'user': 'surveyproduct_db_user',
    'password': '1RkIHhdeJ4NzEwUPj9uWJLsl9y981jhD',
    'database': 'surveyproduct_db',
    'sslmode': 'require'
}

# 表迁移顺序（考虑外键依赖）
TABLES_ORDER = [
    'alembic_version',
    'users',
    'organizations',
    'tags',
    'categories',
    'departments',
    'organization_members',
    'questions',
    'surveys',
    'participants',
    'question_tags',
    'survey_questions',
    'survey_answers'
]

# 数据类型转换映射
def convert_mysql_to_postgres(table_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """将MySQL数据转换为PostgreSQL兼容格式"""
    converted = row_data.copy()
    
    # MySQL的tinyint(1)转换为PostgreSQL的BOOLEAN
    if table_name == 'users':
        if 'is_active' in converted and converted['is_active'] is not None:
            converted['is_active'] = bool(converted['is_active'])
    
    if table_name == 'organizations':
        if 'is_active' in converted and converted['is_active'] is not None:
            converted['is_active'] = bool(converted['is_active'])
        if 'is_public' in converted and converted['is_public'] is not None:
            converted['is_public'] = bool(converted['is_public'])
    
    if table_name == 'departments':
        if 'is_active' in converted and converted['is_active'] is not None:
            converted['is_active'] = bool(converted['is_active'])
    
    if table_name == 'categories':
        if 'is_active' in converted and converted['is_active'] is not None:
            converted['is_active'] = bool(converted['is_active'])
    
    if table_name == 'questions':
        if 'is_required' in converted and converted['is_required'] is not None:
            converted['is_required'] = bool(converted['is_required'])
    
    # 处理NULL值
    for key, value in converted.items():
        if value == 'NULL' or value == '':
            converted[key] = None
        elif key in ['created_at', 'updated_at'] and value:
            # 确保datetime格式正确
            if isinstance(value, str):
                try:
                    converted[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    converted[key] = None
    
    return converted

def connect_mysql():
    """连接MySQL数据库"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        print("✓ 成功连接到MySQL数据库")
        return connection
    except Exception as e:
        print(f"✗ 连接MySQL数据库失败: {e}")
        sys.exit(1)

def connect_postgresql():
    """连接PostgreSQL数据库"""
    try:
        # 创建连接字符串
        conn_str = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}?sslmode={POSTGRES_CONFIG.get('sslmode', 'prefer')}"
        connection = psycopg2.connect(conn_str)
        print("✓ 成功连接到PostgreSQL数据库")
        return connection
    except Exception as e:
        print(f"✗ 连接PostgreSQL数据库失败: {e}")
        sys.exit(1)

def get_table_data_mysql(connection, table_name: str) -> List[Dict[str, Any]]:
    """从MySQL获取表数据"""
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            print(f"✓ 从MySQL获取{table_name}表数据: {len(data)}条记录")
            return data
    except Exception as e:
        print(f"✗ 从MySQL获取{table_name}表数据失败: {e}")
        return []

def insert_data_postgresql(connection, table_name: str, data: List[Dict[str, Any]]):
    """向PostgreSQL插入数据"""
    if not data:
        print(f"跳过{table_name}表：无数据")
        return
    
    try:
        with connection.cursor() as cursor:
            for row in data:
                # 转换数据格式
                converted_row = convert_mysql_to_postgres(table_name, row)
                
                # 构建INSERT语句
                columns = list(converted_row.keys())
                placeholders = ['%s'] * len(columns)
                values = list(converted_row.values())
                
                # 处理JSON字段
                if table_name in ['survey_answers', 'questions'] and 'answers' in converted_row:
                    answers_data = converted_row['answers']
                    if isinstance(answers_data, str):
                        try:
                            # 尝试解析JSON字符串
                            converted_row['answers'] = json.loads(answers_data)
                        except:
                            pass
                    if isinstance(converted_row['answers'], dict):
                        values[columns.index('answers')] = json.dumps(converted_row['answers'])
                
                if table_name == 'questions' and 'options' in converted_row:
                    options_data = converted_row['options']
                    if isinstance(options_data, str):
                        try:
                            # 尝试解析JSON字符串
                            converted_row['options'] = json.loads(options_data)
                        except:
                            pass
                    if isinstance(converted_row['options'], (list, dict)):
                        values[columns.index('options')] = json.dumps(converted_row['options'])
                
                insert_query = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                    ON CONFLICT DO NOTHING
                """
                
                cursor.execute(insert_query, values)
            
            connection.commit()
            print(f"✓ 向PostgreSQL插入{table_name}表数据: {len(data)}条记录")
    except Exception as e:
        print(f"✗ 向PostgreSQL插入{table_name}表数据失败: {e}")
        connection.rollback()

def main():
    """主函数"""
    print("开始数据迁移：MySQL → PostgreSQL")
    print("=" * 50)
    
    # 连接数据库
    mysql_conn = connect_mysql()
    postgres_conn = connect_postgresql()
    
    try:
        # 按照依赖顺序迁移数据
        for table_name in TABLES_ORDER:
            print(f"\n正在迁移表: {table_name}")
            data = get_table_data_mysql(mysql_conn, table_name)
            if data:
                insert_data_postgresql(postgres_conn, table_name, data)
            else:
                print(f"跳过{table_name}表：无数据")
        
        print("\n" + "=" * 50)
        print("✓ 数据迁移完成！")
        
    except Exception as e:
        print(f"\n✗ 数据迁移失败: {e}")
        sys.exit(1)
    finally:
        mysql_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    main()