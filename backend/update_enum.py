#!/usr/bin/env python3
"""
更新coach_type enum类型
"""
import asyncio
import asyncpg
from app.core.config import settings

async def update_enum():
    conn = await asyncpg.connect(settings.DATABASE_URL)

    try:
        print("🔧 开始更新coach_type enum...")

        # 1. 添加新enum值到现有类型
        await conn.execute("ALTER TYPE coach_type ADD VALUE IF NOT EXISTS 'sage'")
        await conn.execute("ALTER TYPE coach_type ADD VALUE IF NOT EXISTS 'companion'")
        await conn.execute("ALTER TYPE coach_type ADD VALUE IF NOT EXISTS 'expert'")

        print("✅ 新enum值添加成功!")

        # 2. 检查结果
        result = await conn.fetch("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'coach_type'
            ORDER BY e.enumsortorder
        """)

        print("\n当前的coach_type enum值:")
        for row in result:
            print(f"  - {row['enumlabel']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_enum())
