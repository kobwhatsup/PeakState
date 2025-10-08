"""
知识库预答案生成脚本
生成常见问题的预答案，存入Qdrant向量数据库

用途：
- 为L3缓存层提供预生成的答案
- 降低简单问题的AI调用成本
- 提升常见问题的响应速度
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger


# 常见问题数据库 (100+条)
KNOWLEDGE_BASE = [
    # ===== 问候类 (10条) =====
    {
        "q": "你好",
        "a": "你好！我是你的AI健康教练，很高兴见到你！😊\n\n我可以帮你:\n• 查看和分析健康数据\n• 提供个性化建议\n• 回答健康相关问题\n\n有什么我可以帮助的吗？",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "早上好",
        "a": "早上好！☀️ 新的一天开始了，希望你精力充沛！\n\n今天有什么健康目标吗？我可以帮你制定计划。",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "晚上好",
        "a": "晚上好！🌙 辛苦了一天，是时候放松一下了。\n\n需要我帮你查看今天的健康数据吗？或者给你一些助眠建议？",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "嗨",
        "a": "嗨！我是你的AI健康教练，随时为你服务！\n\n有什么我可以帮助的吗？",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "hi",
        "a": "Hi! I'm your AI health coach. How can I help you today?",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "hello",
        "a": "Hello! Nice to meet you! I'm here to help you with your health and wellness journey. What can I do for you?",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "在吗",
        "a": "在的！我24小时在线，随时为你服务。有什么需要帮助的吗？",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "你是谁",
        "a": "我是你的AI健康教练！🤖\n\n我的功能：\n• 分析你的健康数据（睡眠、心率、运动等）\n• 提供个性化的健康建议\n• 回答健康相关问题\n• 帮助你建立更好的生活习惯\n\n我使用先进的AI技术，但也有一些限制：我不能替代医生的诊断，遇到严重健康问题请及时就医。",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "你能做什么",
        "a": "我能帮你做这些事：\n\n📊 **数据分析**\n• 查看睡眠、心率、运动数据\n• 分析健康趋势\n• 评估能量水平\n\n💡 **个性化建议**\n• 改善睡眠质量\n• 提升能量水平\n• 优化生活习惯\n\n❤️ **情感支持**\n• 倾听你的烦恼\n• 提供减压建议\n• 帮助你建立积极心态\n\n有什么具体需要帮助的吗？",
        "intent": "greeting",
        "complexity": 1
    },
    {
        "q": "谢谢",
        "a": "不客气！😊 很高兴能帮到你。\n\n如果还有其他问题，随时问我！我会一直在这里支持你。",
        "intent": "confirmation",
        "complexity": 1
    },

    # ===== 数据查询类 (20条) =====
    {
        "q": "我的睡眠怎么样",
        "a": "让我帮你查看最近的睡眠数据...\n\n（正在调取你的睡眠数据）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "查看我的睡眠数据",
        "a": "好的，正在为你调取睡眠数据...\n\n（查询中，请稍候）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "我昨晚睡得好吗",
        "a": "让我查看你昨晚的睡眠情况...\n\n（正在分析昨晚的睡眠数据）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "查看心率",
        "a": "正在为你调取心率数据...\n\n（查询中）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "我的心率正常吗",
        "a": "让我帮你查看心率数据并评估...\n\n（正在分析）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "显示我的运动数据",
        "a": "好的，正在调取你的运动统计...\n\n（查询中）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "我今天走了多少步",
        "a": "让我查看你今天的步数...\n\n（正在查询步数数据）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "我的健康数据",
        "a": "正在为你汇总健康数据...\n\n（查询中，包括睡眠、心率、运动等）",
        "intent": "data_query",
        "complexity": 3
    },
    {
        "q": "最近睡眠质量如何",
        "a": "让我分析你最近的睡眠质量趋势...\n\n（正在分析最近7天的数据）",
        "intent": "data_query",
        "complexity": 4
    },
    {
        "q": "我的能量水平",
        "a": "正在评估你的能量水平...\n\n（综合分析睡眠、活动、心率数据）",
        "intent": "data_query",
        "complexity": 4
    },

    # ===== 建议请求类 (30条) =====
    {
        "q": "如何改善睡眠",
        "a": "改善睡眠可以从以下几个方面入手：\n\n🌙 **作息规律**\n• 每天同一时间睡觉和起床\n• 包括周末也要保持规律\n\n📱 **睡前准备**\n• 睡前1小时避免蓝光（手机、电脑）\n• 做一些放松活动（阅读、冥想）\n\n🛏️ **睡眠环境**\n• 保持房间凉爽（18-22°C）\n• 确保黑暗和安静\n• 舒适的床品\n\n☕ **饮食注意**\n• 下午3点后避免咖啡因\n• 睡前2-3小时不要大量进食\n\n需要更具体的个性化建议吗？我可以根据你的数据给出针对性方案。",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "如何提高能量",
        "a": "提升能量水平的方法：\n\n⚡ **优质睡眠**\n• 保证7-8小时睡眠\n• 睡眠质量比时长更重要\n\n🏃 **规律运动**\n• 每天30分钟中等强度运动\n• 运动能提升整体能量水平\n\n🥗 **健康饮食**\n• 多吃全谷物、蔬果\n• 少吃加工食品和糖\n• 保持水分充足\n\n⏰ **能量管理**\n• 识别你的能量高峰期\n• 在高峰期处理重要任务\n• 适时休息充电\n\n需要我分析你的数据，制定个性化能量提升方案吗？",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "如何减压",
        "a": "减压的有效方法：\n\n🧘 **正念冥想**\n• 每天10-15分钟冥想\n• 专注呼吸，放松身心\n\n🚶 **适度运动**\n• 散步、瑜伽、慢跑\n• 运动能释放内啡肽\n\n🎵 **放松活动**\n• 听音乐\n• 阅读\n• 与朋友交流\n\n💤 **充足睡眠**\n• 睡眠不足会增加压力\n• 保证规律作息\n\n✍️ **情绪日记**\n• 写下压力来源\n• 记录应对策略\n\n需要我帮你制定减压计划吗？",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "如何快速入睡",
        "a": "快速入睡的技巧：\n\n🌡️ **4-7-8呼吸法**\n1. 用鼻子吸气4秒\n2. 屏住呼吸7秒\n3. 用嘴呼气8秒\n4. 重复3-4次\n\n🧠 **认知方法**\n• 数羊或倒数\n• 想象平静的场景\n• 身体扫描放松法\n\n🛏️ **环境优化**\n• 降低温度到18-20°C\n• 完全黑暗\n• 白噪音或自然声\n\n📵 **睡前习惯**\n• 关闭所有屏幕\n• 阅读纸质书\n• 温水泡脚\n\n如果长期失眠，建议咨询医生。需要我根据你的数据给出更具体建议吗？",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "如何保持专注",
        "a": "提升专注力的方法：\n\n⏱️ **番茄工作法**\n• 专注工作25分钟\n• 休息5分钟\n• 4个番茄后休息15-30分钟\n\n🎯 **单任务模式**\n• 一次只做一件事\n• 关闭通知和干扰\n\n🧠 **优化大脑状态**\n• 充足睡眠（7-8小时）\n• 规律运动\n• 健康饮食\n\n☕ **策略性休息**\n• 每90分钟休息一次\n• 短暂走动或伸展\n\n📱 **数字排毒**\n• 固定时间查看手机\n• 使用专注类APP\n\n需要帮你制定专注力提升计划吗？",
        "intent": "advice_request",
        "complexity": 5
    },

    # ===== 情感支持类 (15条) =====
    {
        "q": "我很焦虑",
        "a": "我理解你现在的感受，焦虑确实很难受。💙\n\n首先，深呼吸几次，让自己平静下来。\n\n**一些可以尝试的方法：**\n\n🫂 **接纳情绪**\n• 焦虑是正常的情绪\n• 不要责备自己\n\n🧘 **立即缓解**\n• 深呼吸5次（4秒吸-7秒屏息-8秒呼）\n• 找一个安全的地方坐下\n• 描述周围5个可见物体（转移注意力）\n\n💭 **长期应对**\n• 识别焦虑来源\n• 写下担心的事情\n• 与信任的人交流\n\n如果焦虑持续且严重影响生活，建议寻求专业心理咨询。\n\n我在这里陪你，有什么想聊的吗？",
        "intent": "emotional_support",
        "complexity": 6
    },
    {
        "q": "压力很大",
        "a": "我能感受到你的压力。💙 让我们一起来应对。\n\n**立即缓解压力：**\n\n🌊 **5分钟放松**\n1. 找一个安静的地方\n2. 闭上眼睛深呼吸\n3. 想象压力随呼气离开身体\n\n✍️ **压力清单**\n• 写下所有压力来源\n• 分类：可控 vs 不可控\n• 专注于可控的部分\n\n🎯 **分解任务**\n• 将大任务拆分成小步骤\n• 每完成一步就奖励自己\n\n🤝 **寻求支持**\n• 与朋友或家人交流\n• 必要时寻求专业帮助\n\n记住，你不是一个人在战斗。想聊聊压力的具体来源吗？",
        "intent": "emotional_support",
        "complexity": 6
    },
    {
        "q": "我很累",
        "a": "听起来你确实需要好好休息了。💙\n\n**立即行动：**\n\n😴 **如果可能，休息一下**\n• 小睡15-20分钟\n• 或者简单地闭目养神\n\n💧 **补充能量**\n• 喝一杯水（脱水会导致疲劳）\n• 吃点健康零食（坚果、水果）\n\n🚶 **轻度活动**\n• 短暂散步5-10分钟\n• 简单伸展运动\n\n**长期改善：**\n• 检查睡眠质量\n• 规律作息\n• 适度运动\n\n需要我分析你的睡眠数据，找出疲劳原因吗？",
        "intent": "emotional_support",
        "complexity": 6
    },
    {
        "q": "心情不好",
        "a": "我很抱歉你现在心情不好。💙 我在这里陪你。\n\n**一些可能有帮助的事情：**\n\n🎵 **转移注意力**\n• 听喜欢的音乐\n• 看搞笑视频\n• 做喜欢的活动\n\n🌞 **改变环境**\n• 出去走走，晒晒太阳\n• 换个环境\n• 接触大自然\n\n🤗 **社交连接**\n• 与朋友聊天\n• 拥抱宠物或亲人\n\n✍️ **情绪日记**\n• 写下感受\n• 不评判，只记录\n\n记住，情绪起伏是正常的。如果持续低落超过两周，建议寻求专业帮助。\n\n想聊聊发生了什么吗？",
        "intent": "emotional_support",
        "complexity": 6
    },

    # ===== 健康知识类 (25条) =====
    {
        "q": "什么是深度睡眠",
        "a": "深度睡眠是睡眠最重要的阶段之一：\n\n🧠 **定义**\n• 非快速眼动睡眠（NREM）第3-4阶段\n• 大脑活动最慢，最难被唤醒的阶段\n\n⚡ **作用**\n• 身体修复和生长\n• 增强免疫系统\n• 巩固记忆\n• 清除大脑代谢废物\n\n⏱️ **时长**\n• 成年人：总睡眠的15-25%\n• 7-8小时睡眠中约1-2小时\n• 主要集中在前半夜\n\n📈 **如何增加**\n• 规律作息\n• 避免睡前饮酒\n• 保持适度运动\n• 睡前放松\n\n需要我分析你的深度睡眠数据吗？",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "什么是REM睡眠",
        "a": "REM睡眠（快速眼动睡眠）：\n\n👁️ **特征**\n• 眼球快速运动\n• 大脑活跃，类似清醒状态\n• 身体肌肉完全放松（睡眠麻痹）\n• 大部分梦境发生在此阶段\n\n🧠 **功能**\n• 处理情绪\n• 巩固学习和记忆\n• 促进创造力\n• 大脑排毒\n\n⏱️ **时长**\n• 占总睡眠的20-25%\n• 7-8小时睡眠中约1.5-2小时\n• 主要集中在后半夜\n\n📊 **REM vs 深度睡眠**\n• 深度睡眠：身体修复\n• REM睡眠：大脑整理\n• 两者都很重要！\n\n想看看你的REM睡眠数据吗？",
        "intent": "advice_request",
        "complexity": 5
    },
    {
        "q": "什么是心率变异性",
        "a": "心率变异性（HRV）是重要的健康指标：\n\n💓 **定义**\n• 心跳间隔的变化程度\n• 不是心率快慢，而是节奏的变化\n\n🧠 **意义**\n• 反映自律神经系统功能\n• HRV高：身体适应力强，压力应对好\n• HRV低：可能疲劳、压力大、恢复不足\n\n📊 **正常范围**\n• 因人而异，没有绝对标准\n• 重要的是个人基线和趋势\n\n📈 **如何提高HRV**\n• 充足优质睡眠\n• 规律运动（不过度）\n• 压力管理（冥想、呼吸练习）\n• 避免酗酒和吸烟\n\n需要我分析你的HRV数据吗？",
        "intent": "advice_request",
        "complexity": 5
    },

    # 继续添加更多问题... (总共目标100+条)
]


async def generate_knowledge_base():
    """
    生成知识库

    将所有预定义的问答对编码并存入Qdrant
    """
    logger.info("🚀 Starting knowledge base generation...")

    try:
        # 导入依赖
        from app.ai.response_cache import get_response_cache_manager
        from app.ai.response_cache import CacheEntry
        import hashlib
        from datetime import datetime

        # 初始化缓存管理器
        cache_manager = await get_response_cache_manager()
        await cache_manager.initialize()

        logger.info(f"📚 Processing {len(KNOWLEDGE_BASE)} knowledge base entries...")

        success_count = 0
        error_count = 0

        for idx, qa in enumerate(KNOWLEDGE_BASE, 1):
            try:
                # 创建缓存条目
                cache_entry = CacheEntry(
                    query=qa["q"],
                    response=qa["a"],
                    provider="knowledge_base",
                    intent=qa.get("intent", "general"),
                    complexity=qa.get("complexity", 1),
                    tokens_used=0,  # 知识库答案无token成本
                    cached_at=datetime.utcnow().isoformat(),
                    hit_count=0,
                    user_id="system"
                )

                # 编码查询向量
                import asyncio
                loop = asyncio.get_event_loop()
                query_vector = await loop.run_in_executor(
                    None,
                    lambda: cache_manager.sentence_transformer.encode(
                        qa["q"],
                        convert_to_tensor=False
                    ).tolist()
                )

                # 生成点ID
                point_id = hashlib.md5(qa["q"].encode()).hexdigest()

                # 插入到knowledge_base_qa collection
                from qdrant_client.models import PointStruct

                cache_manager.qdrant_client.upsert(
                    collection_name="knowledge_base_qa",
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=query_vector,
                            payload=cache_entry.to_dict()
                        )
                    ]
                )

                success_count += 1

                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(KNOWLEDGE_BASE)} entries processed")

            except Exception as e:
                error_count += 1
                logger.error(f"Failed to process entry {idx}: {qa['q'][:30]}... | Error: {e}")

        # 统计结果
        logger.info("=" * 80)
        logger.info("✅ Knowledge base generation completed!")
        logger.info(f"Total entries: {len(KNOWLEDGE_BASE)}")
        logger.info(f"Success: {success_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Success rate: {success_count/len(KNOWLEDGE_BASE)*100:.1f}%")
        logger.info("=" * 80)

        return success_count, error_count

    except Exception as e:
        logger.error(f"❌ Knowledge base generation failed: {e}")
        raise


async def verify_knowledge_base():
    """
    验证知识库

    测试几个查询，确认知识库正常工作
    """
    logger.info("🔍 Verifying knowledge base...")

    from app.ai.response_cache import get_response_cache_manager

    cache_manager = await get_response_cache_manager()
    await cache_manager.initialize()

    # 测试查询
    test_queries = [
        "你好",
        "如何改善睡眠",
        "我很焦虑",
        "什么是深度睡眠"
    ]

    logger.info(f"Testing {len(test_queries)} queries...")

    for query in test_queries:
        result = await cache_manager._check_l3_cache(query)

        if result:
            logger.info(f"✅ '{query}' -> Found answer (score>0.88)")
        else:
            logger.warning(f"❌ '{query}' -> No answer found")

    logger.info("Verification completed!")


if __name__ == "__main__":
    import sys

    # 命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        # 仅验证
        asyncio.run(verify_knowledge_base())
    else:
        # 生成知识库
        asyncio.run(generate_knowledge_base())

        # 自动验证
        print("\n")
        asyncio.run(verify_knowledge_base())
