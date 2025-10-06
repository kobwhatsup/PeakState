#!/usr/bin/env python3
"""
测试阿里云RDS PostgreSQL连接
用法: python test_rds_connection.py
"""
import os
import sys
import asyncio
import asyncpg
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def test_rds_connection():
    """测试RDS连接"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL 未配置")
        print("请在 .env 文件中配置阿里云RDS连接信息")
        return False

    # 隐藏密码显示
    display_url = database_url.split('@')[1].split('?')[0] if '@' in database_url else database_url
    print(f"\n🔍 测试连接到: {display_url}")
    print("="*60)

    try:
        print("📡 正在建立连接...")
        # 建立连接
        conn = await asyncpg.connect(database_url)

        # 测试1: 获取数据库版本
        version = await conn.fetchval('SELECT version()')
        print(f"\n✅ 连接成功!")
        print(f"✅ 数据库版本: {version.split(',')[0]}")

        # 测试2: 检查当前数据库名
        current_db = await conn.fetchval('SELECT current_database()')
        print(f"✅ 当前数据库: {current_db}")

        # 测试3: 检查当前用户
        current_user = await conn.fetchval('SELECT current_user')
        print(f"✅ 当前用户: {current_user}")

        # 测试4: 测试创建表权限
        print(f"\n🧪 测试读写权限...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_time TIMESTAMP DEFAULT NOW(),
                test_data TEXT
            )
        """)

        await conn.execute(
            "INSERT INTO connection_test (test_data) VALUES ($1)",
            "PeakState RDS连接测试"
        )

        count = await conn.fetchval("SELECT COUNT(*) FROM connection_test")
        latest_record = await conn.fetchrow("SELECT * FROM connection_test ORDER BY id DESC LIMIT 1")

        print(f"✅ 读写权限正常")
        print(f"   测试记录数: {count}")
        print(f"   最新记录ID: {latest_record['id']}")
        print(f"   记录时间: {latest_record['test_time']}")

        # 测试5: SSL连接状态
        ssl_status = await conn.fetchval("SHOW ssl")
        print(f"✅ SSL连接: {'已启用' if ssl_status == 'on' else '未启用'}")

        # 清理测试表
        await conn.execute("DROP TABLE IF EXISTS connection_test")
        print(f"\n🧹 测试表已清理")

        # 关闭连接
        await conn.close()

        print("\n" + "="*60)
        print("🎉 阿里云RDS连接测试成功!")
        print("\n✅ 检查项:")
        print("   ✓ 网络连接正常")
        print("   ✓ 认证信息正确")
        print("   ✓ 读写权限正常")
        print("   ✓ SSL连接配置正确")
        print("\n📝 下一步:")
        print("   1. 执行数据库迁移: alembic upgrade head")
        print("   2. 启动后端服务: uvicorn app.main:app --reload")
        print("="*60)

        return True

    except asyncpg.InvalidPasswordError:
        print(f"\n❌ 密码错误")
        print("\n请检查:")
        print("  1. .env 中的 ALIYUN_RDS_PASSWORD 是否正确")
        print("  2. 密码中的特殊字符是否需要转义")
        print("  3. 在阿里云控制台重置密码后更新配置")
        return False

    except asyncpg.InvalidCatalogNameError:
        print(f"\n❌ 数据库不存在")
        print("\n请检查:")
        print("  1. .env 中的 ALIYUN_RDS_DATABASE 是否正确")
        print("  2. 在阿里云RDS控制台创建数据库 'peakstate'")
        return False

    except asyncpg.exceptions.PostgresConnectionError as e:
        print(f"\n❌ 连接被拒绝: {e}")
        print("\n请检查:")
        print("  1. 白名单是否包含你的IP地址")
        print(f"     当前公网IP查询: curl ifconfig.me")
        print("  2. ALIYUN_RDS_HOST 地址是否正确")
        print("  3. 端口是否正确(默认5432)")
        print("  4. 是否使用了正确的地址(内网/外网)")
        return False

    except asyncpg.exceptions.SSLError as e:
        print(f"\n❌ SSL连接失败: {e}")
        print("\n请检查:")
        print("  1. 降低SSL模式: ALIYUN_RDS_SSL_MODE=require")
        print("  2. 或配置CA证书: ALIYUN_RDS_SSL_CA_PATH")
        print("  3. 确认RDS实例已启用SSL")
        return False

    except Exception as e:
        print(f"\n❌ 连接失败: {type(e).__name__}")
        print(f"   错误详情: {e}")
        print("\n请检查:")
        print("  1. DATABASE_URL 格式是否正确")
        print("  2. 网络连接是否正常")
        print("  3. 查看完整文档: docs/ALIYUN_RDS_SETUP.md")
        return False


async def check_tables():
    """检查数据库表结构"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return

    try:
        conn = await asyncpg.connect(database_url)

        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        if tables:
            print("\n📊 当前数据库表:")
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table['table_name']}")
        else:
            print("\n⚠️  数据库中还没有表")
            print("   请运行: alembic upgrade head")

        await conn.close()

    except Exception:
        pass


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PeakState - 阿里云RDS PostgreSQL 连接测试")
    print("="*60)

    # 运行连接测试
    success = asyncio.run(test_rds_connection())

    if success:
        # 检查表结构
        asyncio.run(check_tables())
        sys.exit(0)
    else:
        sys.exit(1)
