#!/usr/bin/env python3
"""
测试阿里云RDS连接（使用SQLAlchemy）
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# 加载环境变量
load_dotenv()

def test_rds_connection():
    """测试RDS数据库连接"""
    print("\n" + "="*60)
    print("🔍 测试阿里云RDS PostgreSQL连接")
    print("="*60 + "\n")

    # 获取数据库URL
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ 错误: 未找到DATABASE_URL环境变量")
        print("\n请在 .env 文件中配置：")
        print("DATABASE_URL=postgresql://用户名:密码@主机地址:端口/数据库名?sslmode=require")
        return False

    # 隐藏密码显示
    display_url = database_url
    if "@" in database_url and "://" in database_url:
        parts = database_url.split("://")
        if len(parts) == 2:
            auth_host = parts[1].split("@")
            if len(auth_host) == 2:
                user_pass = auth_host[0].split(":")
                if len(user_pass) == 2:
                    display_url = f"{parts[0]}://{user_pass[0]}:****@{auth_host[1]}"

    print(f"📍 连接地址: {display_url}\n")

    try:
        # 创建数据库引擎
        print("1️⃣  正在连接数据库...")
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )

        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功!\n")

            # 2. 检查PostgreSQL版本
            print("2️⃣  检查数据库版本...")
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ 版本: {version.split(',')[0]}\n")

            # 3. 检查当前用户
            print("3️⃣  检查当前用户...")
            result = conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✅ 当前用户: {user}\n")

            # 4. 检查当前数据库
            print("4️⃣  检查当前数据库...")
            result = conn.execute(text("SELECT current_database()"))
            database = result.scalar()
            print(f"✅ 当前数据库: {database}\n")

            # 5. 测试写权限
            print("5️⃣  测试读写权限...")
            try:
                # 创建测试表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS _connection_test (
                        id SERIAL PRIMARY KEY,
                        test_data VARCHAR(100)
                    )
                """))
                conn.commit()

                # 插入测试数据
                conn.execute(text(
                    "INSERT INTO _connection_test (test_data) VALUES (:data)"
                ), {"data": "RDS连接测试成功"})
                conn.commit()

                # 读取测试数据
                result = conn.execute(text("SELECT test_data FROM _connection_test"))
                test_data = result.scalar()

                # 删除测试表
                conn.execute(text("DROP TABLE _connection_test"))
                conn.commit()

                print(f"✅ 读写测试通过: {test_data}\n")

            except Exception as e:
                print(f"❌ 读写测试失败: {e}\n")
                return False

            # 6. 检查SSL连接状态
            print("6️⃣  检查SSL连接状态...")
            try:
                result = conn.execute(text("SHOW ssl"))
                ssl_status = result.scalar()
                print(f"✅ SSL状态: {ssl_status}\n")
            except:
                print("⚠️  无法检查SSL状态（可能不支持此命令）\n")

            # 7. 检查现有表
            print("7️⃣  检查现有数据表...")
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            if tables:
                print(f"✅ 发现 {len(tables)} 个表:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("ℹ️  数据库为空，尚未创建表")
                print("   (这是正常的，需要运行 alembic upgrade head 创建表)\n")

        print("\n" + "="*60)
        print("🎉 RDS连接测试完成!")
        print("="*60)
        print("\n✅ 所有测试通过! 数据库配置正确。\n")
        print("📝 后续步骤:")
        print("  1. 运行数据库迁移: alembic upgrade head")
        print("  2. 启动后端服务: uvicorn app.main:app --reload")
        print("  3. 访问API文档: http://localhost:8000/docs\n")

        return True

    except OperationalError as e:
        print("\n❌ 数据库连接失败!")
        print("="*60)
        print(f"\n错误详情: {e}\n")
        print("💡 常见问题排查:")
        print("  1. 检查RDS实例是否正在运行")
        print("  2. 检查白名单是否包含当前IP地址")
        print("  3. 检查数据库用户名和密码是否正确")
        print("  4. 检查数据库连接地址和端口是否正确")
        print("  5. 检查网络连接是否正常")
        print("  6. 检查是否启用了SSL连接（sslmode=require）\n")
        print("查看详细配置指南: docs/ALIYUN_RDS_SETUP.md\n")
        return False

    except ProgrammingError as e:
        print("\n❌ 数据库操作失败!")
        print("="*60)
        print(f"\n错误详情: {e}\n")
        print("💡 可能的原因:")
        print("  1. 数据库权限不足")
        print("  2. 数据库不存在")
        print("  3. SQL语法错误\n")
        return False

    except Exception as e:
        print("\n❌ 未知错误!")
        print("="*60)
        print(f"\n错误详情: {e}\n")
        return False

if __name__ == "__main__":
    success = test_rds_connection()
    sys.exit(0 if success else 1)
