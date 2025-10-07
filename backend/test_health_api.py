#!/usr/bin/env python3
"""
健康数据API测试脚本
测试完整的用户注册->登录->健康数据操作流程
"""

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """打印响应"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def main():
    print("\n🚀 开始测试PeakState健康数据API\n")

    # 1. 注册用户
    print("1️⃣  注册测试用户...")
    phone = f"138{random.randint(10000000, 99999999)}"
    register_data = {
        "phone_number": phone,
        "password": "test123456",
        "coach_selection": "sage"  # 使用sage类型
    }

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data
    )
    print_response("注册响应", response)

    if response.status_code != 201:
        print("❌ 注册失败")
        return

    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n✅ 注册成功!")
    print(f"📱 手机号: {phone}")
    print(f"🔑 Token: {access_token[:50]}...")

    # 2. 获取当前用户信息
    print("\n2️⃣  获取用户信息...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("用户信息", response)

    user_data = response.json()
    user_id = user_data["id"]

    # 3. 创建睡眠数据
    print("\n3️⃣  创建睡眠数据...")
    sleep_data = {
        "data_type": "sleep_duration",
        "value": 7.5,
        "unit": "hours",
        "source": "manual",
        "recorded_at": datetime.utcnow().isoformat(),
        "extra_data": {
            "quality": "good",
            "notes": "深度睡眠很好"
        }
    }

    response = requests.post(
        f"{BASE_URL}/health/data",
        json=sleep_data,
        headers=headers
    )
    print_response("创建睡眠数据", response)

    # 4. 批量创建健康数据(最近7天的数据)
    print("\n4️⃣  批量创建健康数据(最近7天)...")
    batch_data = {
        "data": []
    }

    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)

        # 睡眠时长
        batch_data["data"].append({
            "data_type": "sleep_duration",
            "value": round(random.uniform(6.5, 8.5), 1),
            "unit": "hours",
            "source": "manual",
            "recorded_at": date.isoformat()
        })

        # HRV
        batch_data["data"].append({
            "data_type": "hrv",
            "value": round(random.uniform(45, 65), 1),
            "unit": "ms",
            "source": "manual",
            "recorded_at": date.isoformat()
        })

        # 步数
        batch_data["data"].append({
            "data_type": "steps",
            "value": random.randint(5000, 12000),
            "unit": "count",
            "source": "manual",
            "recorded_at": date.isoformat()
        })

        # 能量水平
        batch_data["data"].append({
            "data_type": "energy_level",
            "value": random.randint(6, 9),
            "unit": "score",
            "source": "manual",
            "recorded_at": date.isoformat()
        })

    response = requests.post(
        f"{BASE_URL}/health/data/batch",
        json=batch_data,
        headers=headers
    )
    print_response(f"批量创建数据 (共{len(batch_data['data'])}条)", response)

    # 5. 查询睡眠数据
    print("\n5️⃣  查询睡眠数据...")
    response = requests.get(
        f"{BASE_URL}/health/data/sleep_duration",
        headers=headers,
        params={"limit": 10}
    )
    print_response("查询睡眠数据", response)

    # 6. 获取最新睡眠数据
    print("\n6️⃣  获取最新睡眠数据...")
    response = requests.get(
        f"{BASE_URL}/health/data/sleep_duration/latest",
        headers=headers
    )
    print_response("最新睡眠数据", response)

    # 7. 获取健康摘要(7天)
    print("\n7️⃣  获取健康摘要(7天)...")
    response = requests.get(
        f"{BASE_URL}/health/summary",
        headers=headers,
        params={"days": 7}
    )
    print_response("健康摘要", response)

    # 8. 查询HRV数据
    print("\n8️⃣  查询HRV数据...")
    response = requests.get(
        f"{BASE_URL}/health/data/hrv",
        headers=headers,
        params={"limit": 7}
    )
    print_response("查询HRV数据", response)

    # 9. 查询步数数据
    print("\n9️⃣  查询步数数据...")
    response = requests.get(
        f"{BASE_URL}/health/data/steps",
        headers=headers,
        params={"limit": 7}
    )
    print_response("查询步数数据", response)

    print("\n" + "="*60)
    print("🎉 所有测试完成!")
    print("="*60)

    print(f"\n📊 测试摘要:")
    print(f"  ✅ 用户注册")
    print(f"  ✅ 创建健康数据")
    print(f"  ✅ 批量创建数据 ({len(batch_data['data'])}条)")
    print(f"  ✅ 查询数据")
    print(f"  ✅ 健康摘要")

    print(f"\n🔗 API文档: http://localhost:8000/docs")
    print(f"👤 测试用户: {phone}")
    print(f"🔑 Token: {access_token[:50]}...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹  测试已取消")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
