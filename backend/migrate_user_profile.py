#!/usr/bin/env python3
"""
手动执行用户画像字段迁移
用于解决alembic架构不兼容问题
"""

import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 解析DATABASE_URL
# postgresql://user:password@host:port/dbname?sslmode=require
url_parts = DATABASE_URL.replace("postgresql://", "").split("@")
user_pass = url_parts[0].split(":")
host_port_db = url_parts[1].split("/")
host_port = host_port_db[0].split(":")
dbname_ssl = host_port_db[1].split("?")

USER = user_pass[0]
PASSWORD = user_pass[1]
HOST = host_port[0]
PORT = host_port[1]
DBNAME = dbname_ssl[0]

# SQL迁移语句
MIGRATION_SQL = """
-- 添加用户画像字段
DO $$
BEGIN
    -- 添加age字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='age') THEN
        ALTER TABLE users ADD COLUMN age INTEGER NULL;
        COMMENT ON COLUMN users.age IS '年龄';
    END IF;

    -- 添加gender字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='gender') THEN
        ALTER TABLE users ADD COLUMN gender VARCHAR(20) NULL;
        COMMENT ON COLUMN users.gender IS '性别(male/female/other/prefer_not_to_say)';
    END IF;

    -- 添加occupation字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='occupation') THEN
        ALTER TABLE users ADD COLUMN occupation VARCHAR(100) NULL;
        COMMENT ON COLUMN users.occupation IS '职业';
    END IF;

    -- 添加health_goals字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='health_goals') THEN
        ALTER TABLE users ADD COLUMN health_goals VARCHAR(500) NULL;
        COMMENT ON COLUMN users.health_goals IS '健康目标(逗号分隔)';
    END IF;
END $$;
"""

def main():
    print("🔄 开始执行用户画像字段迁移...")
    print(f"📍 连接数据库: {HOST}:{PORT}/{DBNAME}")

    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            sslmode='require'
        )

        cursor = conn.cursor()

        # 执行迁移
        print("⚙️  执行SQL迁移...")
        cursor.execute(MIGRATION_SQL)
        conn.commit()

        # 验证字段是否添加成功
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('age', 'gender', 'occupation', 'health_goals')
            ORDER BY column_name;
        """)

        results = cursor.fetchall()

        if results:
            print("\n✅ 迁移成功! 新增字段:")
            for row in results:
                print(f"   - {row[0]} ({row[1]}, nullable: {row[2]})")
        else:
            print("\n⚠️  警告: 未找到新字段,可能已存在")

        cursor.close()
        conn.close()

        print("\n🎉 迁移完成!")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
