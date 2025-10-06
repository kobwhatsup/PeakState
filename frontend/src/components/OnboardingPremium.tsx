import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Sparkles, Zap, Shield } from "lucide-react";
import { Button } from "./ui/button";
import { CoachAvatarPremium } from "./CoachAvatarPremium";

interface OnboardingPremiumProps {
  onComplete: (coachType: "wise" | "companion" | "expert") => void;
}

export function OnboardingPremium({ onComplete }: OnboardingPremiumProps) {
  const [currentScreen, setCurrentScreen] = useState(0);
  const [selectedCoach, setSelectedCoach] = useState<"wise" | "companion" | "expert" | null>(null);

  const nextScreen = () => {
    if (currentScreen < 4) {
      setCurrentScreen(currentScreen + 1);
    } else if (selectedCoach) {
      onComplete(selectedCoach);
    }
  };

  const selectCoach = (type: "wise" | "companion" | "expert") => {
    setSelectedCoach(type);
    setTimeout(() => nextScreen(), 1200);
  };

  const coaches = [
    { 
      type: "wise" as const, 
      name: "深思", 
      description: "理性分析 · 洞察本质",
      trait: "适合追求深度思考的你"
    },
    { 
      type: "companion" as const, 
      name: "温言", 
      description: "温暖陪伴 · 正向激励",
      trait: "适合需要情感支持的你"
    },
    { 
      type: "expert" as const, 
      name: "明策", 
      description: "精准高效 · 目标导向",
      trait: "适合追求效率提升的你"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0C] flex items-center justify-center p-6 relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute w-96 h-96 rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)",
            top: "-10%",
            left: "-10%",
            filter: "blur(60px)"
          }}
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute w-96 h-96 rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(240, 147, 251, 0.08) 0%, transparent 70%)",
            bottom: "-10%",
            right: "-10%",
            filter: "blur(60px)"
          }}
          animate={{
            x: [0, -50, 0],
            y: [0, -30, 0],
            scale: [1, 1.3, 1]
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <AnimatePresence mode="wait">
        {/* Screen 1: 欢迎页 */}
        {currentScreen === 0 && (
          <motion.div
            key="screen-0"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="text-center max-w-lg relative z-10"
          >
            <motion.div
              className="mb-16 relative"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            >
              <div className="relative inline-block">
                {/* 环绕光环 */}
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute inset-0 rounded-full border-2"
                    style={{
                      borderColor: `rgba(102, 126, 234, ${0.3 - i * 0.1})`,
                      scale: 1 + i * 0.3
                    }}
                    animate={{
                      rotate: 360,
                      opacity: [0.3, 0.6, 0.3]
                    }}
                    transition={{
                      rotate: { duration: 20 - i * 5, repeat: Infinity, ease: "linear" },
                      opacity: { duration: 3, repeat: Infinity, delay: i * 0.5 }
                    }}
                  />
                ))}
                
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center relative overflow-hidden backdrop-blur-xl"
                  style={{ boxShadow: "0 20px 60px rgba(102, 126, 234, 0.4)" }}
                >
                  <motion.div
                    className="absolute inset-0"
                    animate={{
                      background: [
                        "radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3) 0%, transparent 50%)",
                        "radial-gradient(circle at 70% 70%, rgba(255,255,255,0.3) 0%, transparent 50%)",
                        "radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3) 0%, transparent 50%)"
                      ]
                    }}
                    transition={{ duration: 5, repeat: Infinity }}
                  />
                  <Sparkles className="w-16 h-16 text-white relative z-10" strokeWidth={1.5} />
                </div>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
            >
              <h1 className="mb-6 bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
                遇见更好的自己
              </h1>
              <p className="text-[#8E8E93] mb-16 leading-relaxed">
                开启由AI驱动的精力管理之旅<br/>
                <span className="text-sm opacity-70">科学 · 专业 · 个性化</span>
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
            >
              <Button 
                onClick={nextScreen}
                className="group relative bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:shadow-[0_0_40px_rgba(102,126,234,0.4)] text-white px-12 py-7 rounded-full overflow-hidden transition-all duration-300"
              >
                <span className="relative z-10 flex items-center gap-2">
                  开始探索
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    →
                  </motion.span>
                </span>
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-[#764ba2] to-[#667eea]"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
              </Button>
            </motion.div>
          </motion.div>
        )}

        {/* Screen 2-3: 价值呈现（合并展示） */}
        {(currentScreen === 1 || currentScreen === 2) && (
          <motion.div
            key={`screen-${currentScreen}`}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-2xl relative z-10"
          >
            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {/* 卡片1 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-[#667eea]/20 to-transparent rounded-3xl blur-xl group-hover:blur-2xl transition-all" />
                <div className="relative bg-[#1C1C1E]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:border-[#667eea]/50 transition-all">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center mb-6"
                    style={{ boxShadow: "0 10px 30px rgba(102, 126, 234, 0.3)" }}
                  >
                    <Shield className="w-8 h-8 text-white" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-white mb-3">全维度数据整合</h3>
                  <p className="text-[#8E8E93] leading-relaxed">
                    深度分析你的睡眠、运动、心率等生理指标，结合情绪与压力状态，构建完整的精力画像
                  </p>
                </div>
              </motion.div>

              {/* 卡片2 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-[#f093fb]/20 to-transparent rounded-3xl blur-xl group-hover:blur-2xl transition-all" />
                <div className="relative bg-[#1C1C1E]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:border-[#f093fb]/50 transition-all">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#f093fb] to-[#f5576c] flex items-center justify-center mb-6"
                    style={{ boxShadow: "0 10px 30px rgba(240, 147, 251, 0.3)" }}
                  >
                    <Zap className="w-8 h-8 text-white" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-white mb-3">智能主动规划</h3>
                  <p className="text-[#8E8E93] leading-relaxed">
                    AI教练基于你的精力曲线，主动优化日程安排，确保重要任务在最佳状态下完成
                  </p>
                </div>
              </motion.div>
            </div>

            <div className="text-center">
              <Button 
                onClick={nextScreen}
                variant="ghost"
                className="text-white/60 hover:text-white hover:bg-white/5 px-8 py-6 rounded-full"
              >
                继续 →
              </Button>
            </div>
          </motion.div>
        )}

        {/* Screen 4: 教练选择 */}
        {currentScreen === 3 && (
          <motion.div
            key="screen-3"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-3xl w-full relative z-10"
          >
            <div className="text-center mb-12">
              <motion.h2 
                className="mb-4 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                选择你的AI教练
              </motion.h2>
              <motion.p 
                className="text-[#8E8E93]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                每位教练都拥有独特的指导风格与智慧
              </motion.p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              {coaches.map((coach, index) => (
                <motion.button
                  key={coach.type}
                  onClick={() => selectCoach(coach.type)}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  whileHover={{ scale: 1.03, y: -5 }}
                  whileTap={{ scale: 0.98 }}
                  className={`relative group text-center transition-all duration-300 ${
                    selectedCoach === coach.type ? 'scale-105' : ''
                  }`}
                >
                  <div className={`absolute inset-0 rounded-3xl transition-all duration-500 ${
                    selectedCoach === coach.type 
                      ? 'bg-gradient-to-br from-[#667eea]/30 to-[#764ba2]/30 blur-2xl' 
                      : 'bg-[#1C1C1E]/40 blur-xl group-hover:blur-2xl'
                  }`} />
                  
                  <div className={`relative bg-[#1C1C1E]/60 backdrop-blur-2xl border rounded-3xl p-8 transition-all duration-300 ${
                    selectedCoach === coach.type
                      ? 'border-[#667eea] shadow-[0_0_40px_rgba(102,126,234,0.3)]'
                      : 'border-white/10 group-hover:border-white/20'
                  }`}>
                    <div className="mb-6 flex justify-center">
                      <CoachAvatarPremium 
                        type={coach.type} 
                        size="xl" 
                        isActive={selectedCoach === coach.type} 
                      />
                    </div>
                    
                    <h3 className="text-white mb-2">{coach.name}</h3>
                    <p className="text-[#8E8E93] mb-3">{coach.description}</p>
                    <p className="text-sm text-white/40">{coach.trait}</p>

                    {selectedCoach === coach.type && (
                      <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="absolute -top-3 -right-3 w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center shadow-lg"
                      >
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                          <path d="M4 10L8 14L16 6" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </motion.div>
                    )}
                  </div>
                </motion.button>
              ))}
            </div>

            <AnimatePresence>
              {selectedCoach && (
                <motion.div
                  initial={{ opacity: 0, y: 30, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-[#667eea]/20 to-[#764ba2]/20 rounded-3xl blur-2xl" />
                  <div className="relative bg-[#1C1C1E]/80 backdrop-blur-2xl border border-[#667eea]/30 rounded-3xl p-8">
                    <div className="flex items-start gap-4">
                      <CoachAvatarPremium type={selectedCoach} size="md" isActive />
                      <div className="flex-1 text-left">
                        <motion.p 
                          className="text-white mb-3 leading-relaxed"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          你好，很高兴成为你的AI教练。
                        </motion.p>
                        <motion.p 
                          className="text-white/80 leading-relaxed"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.4 }}
                        >
                          我将基于你的独特数据，为你提供最适合的精力管理方案。准备好开始了吗？
                        </motion.p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Screen 5: 授权与订阅 */}
        {currentScreen === 4 && (
          <motion.div
            key="screen-4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-md w-full relative z-10"
          >
            <div className="text-center mb-10">
              <h2 className="mb-3 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                开启专属服务
              </h2>
              <p className="text-[#8E8E93]">安全授权，智能守护</p>
            </div>

            {/* 权限卡片 */}
            <div className="space-y-4 mb-10">
              {[
                { icon: "❤️", title: "健康数据", desc: "睡眠质量、运动记录、心率变化", gradient: "from-red-500/20 to-pink-500/20" },
                { icon: "📅", title: "日历同步", desc: "智能分析日程，优化时间分配", gradient: "from-orange-500/20 to-yellow-500/20" }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  className="relative group"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity`} />
                  <div className="relative bg-[#1C1C1E]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 flex items-center gap-4 group-hover:border-white/20 transition-all">
                    <div className="text-3xl">{item.icon}</div>
                    <div className="flex-1 text-left">
                      <h4 className="text-white mb-1">{item.title}</h4>
                      <p className="text-[#8E8E93]">{item.desc}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* 订阅方案 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="relative mb-8"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-[#667eea]/30 to-[#764ba2]/30 rounded-3xl blur-2xl" />
              <div className="relative bg-gradient-to-br from-[#667eea]/10 to-[#764ba2]/10 backdrop-blur-xl border border-[#667eea]/30 rounded-3xl p-8 text-center">
                <div className="inline-block px-4 py-1 bg-[#667eea]/20 rounded-full mb-4">
                  <span className="text-[#667eea]">限时优惠</span>
                </div>
                <div className="mb-4">
                  <span className="text-white/60 line-through mr-3">¥500/月</span>
                  <span className="text-white">¥300/月</span>
                </div>
                <p className="text-[#667eea] mb-2">前7天免费体验</p>
                <p className="text-[#8E8E93]">随时取消 · 无需承诺</p>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Button 
                onClick={nextScreen}
                className="w-full group relative bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:shadow-[0_0_40px_rgba(102,126,234,0.4)] text-white py-7 rounded-full overflow-hidden transition-all duration-300"
              >
                <span className="relative z-10">立即开始免费试用</span>
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-[#764ba2] to-[#667eea]"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
              </Button>
              
              <p className="text-[#8E8E93] text-center mt-4">
                继续即表示同意 <span className="text-white/40">服务条款</span> 和 <span className="text-white/40">隐私政策</span>
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
