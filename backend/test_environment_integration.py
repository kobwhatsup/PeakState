"""
测试环境数据集成

验证天气API和环境数据采集功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.weather import WeatherService
from app.core.database import get_db_session
from sqlalchemy import select
from app.models.user import User
from app.models.energy import EnvironmentData


async def test_weather_api():
    """测试天气API调用"""
    print("\n" + "="*60)
    print("测试 1: 天气API调用")
    print("="*60)

    weather_service = WeatherService()

    # 测试OpenWeather API (如果配置了)
    if settings.WEATHER_API_KEY:
        print(f"\n使用提供商: {settings.WEATHER_PROVIDER}")
        print(f"API密钥: {settings.WEATHER_API_KEY[:10]}...")

        # 测试北京天气
        print("\n获取北京天气数据...")
        weather_data = await weather_service.get_current_weather("Beijing")

        if weather_data:
            print("✅ 天气数据获取成功!")
            print(f"  位置: {weather_data['location']}")
            print(f"  温度: {weather_data['temperature']}°C")
            print(f"  体感温度: {weather_data['feels_like']}°C")
            print(f"  天气: {weather_data['weather']}")
            print(f"  气压: {weather_data['pressure']} hPa")
            print(f"  湿度: {weather_data['humidity']}%")
            print(f"  空气质量: {weather_data.get('air_quality', 'N/A')}")
            print(f"  时间: {weather_data['timestamp']}")
            return True
        else:
            print("❌ 天气数据获取失败")
            return False
    else:
        print("⚠️  未配置WEATHER_API_KEY，跳过天气API测试")
        print("请在.env文件中添加:")
        print("  WEATHER_API_KEY=your_api_key")
        print("  WEATHER_PROVIDER=openweather  # 或 qweather")
        return False


async def test_environment_data_storage():
    """测试环境数据存储"""
    print("\n" + "="*60)
    print("测试 2: 环境数据存储")
    print("="*60)

    if not settings.WEATHER_API_KEY:
        print("⚠️  跳过（需要先配置WEATHER_API_KEY）")
        return False

    weather_service = WeatherService()

    async for db in get_db_session():
        try:
            # 获取第一个用户
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()

            if not user:
                print("❌ 数据库中没有用户，请先创建用户")
                return False

            print(f"\n使用测试用户: {user.id}")

            # 获取天气数据
            weather_data = await weather_service.get_current_weather("Beijing")
            if not weather_data:
                print("❌ 获取天气数据失败")
                return False

            # 保存到数据库
            print("\n保存环境数据到数据库...")
            env_data = await weather_service.save_environment_data(
                db=db,
                user_id=str(user.id),
                weather_data=weather_data
            )

            if env_data:
                print("✅ 环境数据保存成功!")
                print(f"  记录ID: {env_data.id}")
                print(f"  用户ID: {env_data.user_id}")
                print(f"  位置: {env_data.location}")
                print(f"  温度: {env_data.temperature}°C")
                print(f"  天气: {env_data.weather}")

                # 查询保存的数据
                print("\n查询最近24小时的环境数据...")
                recent_data = await weather_service.get_latest_environment_data(
                    db=db,
                    user_id=str(user.id),
                    hours=24
                )
                print(f"✅ 找到 {len(recent_data)} 条记录")

                return True
            else:
                print("❌ 环境数据保存失败")
                return False

        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_energy_prediction_with_environment():
    """测试精力预测集成环境数据"""
    print("\n" + "="*60)
    print("测试 3: 精力预测集成环境数据")
    print("="*60)

    if not settings.WEATHER_API_KEY:
        print("⚠️  跳过（需要先配置WEATHER_API_KEY）")
        return False

    from app.ai.energy_prediction import EnergyPredictionModel

    async for db in get_db_session():
        try:
            # 获取第一个用户
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()

            if not user:
                print("❌ 数据库中没有用户")
                return False

            print(f"\n使用测试用户: {user.id}")

            # 先采集环境数据
            weather_service = WeatherService()
            env_data = await weather_service.collect_and_save(
                db=db,
                user_id=str(user.id),
                location="Beijing"
            )

            if not env_data:
                print("⚠️  环境数据采集失败，但继续测试精力预测")

            # 测试精力预测
            print("\n执行精力预测...")
            model = EnergyPredictionModel()
            prediction = await model.predict_current_energy(str(user.id), db)

            print("✅ 精力预测成功!")
            print(f"  当前精力: {prediction.energy_level.value} ({prediction.energy_score:.1f}/10)")
            print(f"  置信度: {prediction.confidence:.1%}")
            print(f"\n  影响因素:")
            for factor, value in prediction.factors.items():
                print(f"    {factor}: {value:+.2f}")

            # 检查是否使用了环境数据
            if env_data:
                print(f"\n  环境数据已集成:")
                print(f"    温度: {env_data.temperature}°C")
                print(f"    天气: {env_data.weather}")
                print(f"    气压: {env_data.pressure} hPa")

            return True

        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("环境数据集成测试套件")
    print("="*60)

    results = {
        "天气API调用": await test_weather_api(),
        "环境数据存储": await test_environment_data_storage(),
        "精力预测集成": await test_energy_prediction_with_environment(),
    }

    # 打印测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results.items():
        if result is True:
            status = "✅ 通过"
            passed += 1
        elif result is False:
            status = "❌ 失败"
            failed += 1
        else:
            status = "⚠️  跳过"
            skipped += 1
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")

    if failed == 0 and passed > 0:
        print("\n🎉 所有测试通过!")
    elif skipped > 0:
        print("\n💡 提示: 请配置WEATHER_API_KEY以运行完整测试")


if __name__ == "__main__":
    asyncio.run(main())
