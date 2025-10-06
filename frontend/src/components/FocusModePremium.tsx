import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Pause, Play, Check } from "lucide-react";
import { Button } from "./ui/button";

interface FocusModePremiumProps {
  onExit: () => void;
}

export function FocusModePremium({ onExit }: FocusModePremiumProps) {
  const [duration] = useState(25 * 60);
  const [timeLeft, setTimeLeft] = useState(duration);
  const [isActive, setIsActive] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => time - 1);
      }, 1000);
    } else if (timeLeft === 0 && !isCompleted) {
      setIsCompleted(true);
      setIsActive(false);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeLeft, isCompleted]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return {
      minutes: mins.toString().padStart(2, "0"),
      seconds: secs.toString().padStart(2, "0")
    };
  };

  const progress = ((duration - timeLeft) / duration) * 100;
  const time = formatTime(timeLeft);

  // 呼吸节奏 - 4秒吸气，4秒呼气
  const breatheCycle = 8;
  const breathePhase = (timeLeft % breatheCycle) / breatheCycle;

  return (
    <div className="min-h-screen bg-[#0A0A0C] relative overflow-hidden flex items-center justify-center">
      {/* 动态粒子背景 */}
      <div className="absolute inset-0">
        {/* 主背景渐变 */}
        <motion.div
          className="absolute inset-0"
          animate={{
            background: [
              "radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(118, 75, 162, 0.08) 0%, transparent 50%)",
              "radial-gradient(circle at 80% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 50%), radial-gradient(circle at 20% 50%, rgba(118, 75, 162, 0.08) 0%, transparent 50%)",
              "radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(118, 75, 162, 0.08) 0%, transparent 50%)"
            ]
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* 浮动光球 */}
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-64 h-64 rounded-full"
            style={{
              background: `radial-gradient(circle, ${
                i % 2 === 0 ? "rgba(102, 126, 234, 0.06)" : "rgba(240, 147, 251, 0.06)"
              } 0%, transparent 70%)`,
              filter: "blur(60px)",
              left: `${(i * 25) % 100}%`,
              top: `${(i * 30) % 100}%`
            }}
            animate={{
              x: [0, Math.random() * 100 - 50, 0],
              y: [0, Math.random() * 100 - 50, 0],
              scale: [1, 1.2, 1]
            }}
            transition={{
              duration: 15 + i * 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 1.5
            }}
          />
        ))}

        {/* 网格线 */}
        <div className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: "80px 80px"
          }}
        />
      </div>

      {/* 主内容 */}
      <div className="relative z-10 text-center px-6 max-w-2xl w-full">
        {!isCompleted ? (
          <>
            {/* 呼吸引导圈 */}
            <div className="relative mb-16 mx-auto">
              {/* 外层呼吸光环 */}
              <motion.div
                className="absolute inset-0 flex items-center justify-center"
                animate={{
                  scale: breathePhase < 0.5 ? [1, 1.3] : [1.3, 1],
                  opacity: breathePhase < 0.5 ? [0.3, 0.6] : [0.6, 0.3]
                }}
                transition={{
                  duration: 4,
                  ease: "easeInOut"
                }}
              >
                <div className="w-[500px] h-[500px] rounded-full bg-gradient-to-br from-[#667eea]/20 to-[#764ba2]/20 blur-3xl" />
              </motion.div>

              {/* 进度环 */}
              <svg className="w-[400px] h-[400px] transform -rotate-90 relative">
                {/* 背景环 */}
                <circle
                  cx="200"
                  cy="200"
                  r="180"
                  stroke="rgba(255, 255, 255, 0.03)"
                  strokeWidth="2"
                  fill="none"
                />
                
                {/* 进度环 */}
                <motion.circle
                  cx="200"
                  cy="200"
                  r="180"
                  stroke="url(#progressGradient)"
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 180}
                  strokeDashoffset={2 * Math.PI * 180 * (1 - progress / 100)}
                  style={{
                    filter: "drop-shadow(0 0 20px rgba(102, 126, 234, 0.5))"
                  }}
                />
                
                {/* 呼吸脉冲环 */}
                <motion.circle
                  cx="200"
                  cy="200"
                  r="160"
                  stroke="rgba(102, 126, 234, 0.3)"
                  strokeWidth="1"
                  fill="none"
                  animate={{
                    scale: breathePhase < 0.5 ? [1, 1.1] : [1.1, 1],
                    opacity: [0.3, 0.6, 0.3]
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />

                <defs>
                  <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#667eea" />
                    <stop offset="50%" stopColor="#f093fb" />
                    <stop offset="100%" stopColor="#667eea" />
                  </linearGradient>
                </defs>
              </svg>

              {/* 中心时间显示 */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  {/* 3D时间数字 */}
                  <div className="relative mb-8">
                    <motion.div
                      className="text-white relative z-10"
                      style={{ 
                        fontSize: '6rem',
                        lineHeight: 1,
                        fontVariantNumeric: 'tabular-nums',
                        textShadow: '0 0 40px rgba(102, 126, 234, 0.5), 0 0 80px rgba(102, 126, 234, 0.3)'
                      }}
                      animate={{
                        scale: timeLeft % 60 === 0 ? [1, 1.05, 1] : 1
                      }}
                    >
                      <span className="font-light">{time.minutes}</span>
                      <motion.span 
                        className="mx-2 opacity-60"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      >
                        :
                      </motion.span>
                      <span className="font-light">{time.seconds}</span>
                    </motion.div>
                    
                    {/* 数字倒影 */}
                    <div 
                      className="absolute top-0 left-0 right-0 text-white/10 blur-sm"
                      style={{ 
                        fontSize: '6rem',
                        lineHeight: 1,
                        transform: 'scaleY(-1) translateY(100%)',
                        WebkitMaskImage: 'linear-gradient(transparent 30%, black 100%)'
                      }}
                    >
                      {time.minutes}:{time.seconds}
                    </div>
                  </div>

                  {/* 状态文字 */}
                  <motion.div
                    animate={{ opacity: [0.6, 1, 0.6] }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="space-y-2"
                  >
                    <p className="text-white/80">
                      {isActive ? "保持专注" : "已暂停"}
                    </p>
                    
                    {/* 呼吸引导 */}
                    <motion.p 
                      className="text-[#667eea] text-sm"
                      animate={{
                        opacity: breathePhase < 0.5 ? [0.5, 1] : [1, 0.5]
                      }}
                      transition={{ duration: 4 }}
                    >
                      {breathePhase < 0.5 ? "缓缓吸气..." : "慢慢呼气..."}
                    </motion.p>
                  </motion.div>
                </div>
              </div>

              {/* 环绕粒子 */}
              {isActive && [...Array(12)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1.5 h-1.5 rounded-full bg-[#667eea]"
                  style={{
                    left: "50%",
                    top: "50%",
                    transformOrigin: "0 0"
                  }}
                  animate={{
                    rotate: 360,
                    opacity: [0, 1, 0]
                  }}
                  transition={{
                    rotate: {
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                      delay: i * (20 / 12)
                    },
                    opacity: {
                      duration: 4,
                      repeat: Infinity,
                      delay: i * 0.3
                    }
                  }}
                >
                  <div style={{ transform: `translate(-50%, -50%) translate(200px, 0)` }} />
                </motion.div>
              ))}
            </div>

            {/* 控制按钮 */}
            <div className="flex items-center justify-center gap-6">
              <Button
                onClick={() => setIsActive(!isActive)}
                variant="ghost"
                size="lg"
                className="relative group w-20 h-20 rounded-full bg-white/5 hover:bg-white/10 backdrop-blur-xl border border-white/10 hover:border-white/20 transition-all"
              >
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-[#667eea]/20 to-[#764ba2]/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                {isActive ? (
                  <Pause className="w-8 h-8 text-white relative z-10" strokeWidth={1.5} />
                ) : (
                  <Play className="w-8 h-8 text-white relative z-10" strokeWidth={1.5} />
                )}
              </Button>
            </div>

            {/* 环境音乐提示 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="mt-12 flex items-center justify-center gap-3 text-white/30"
            >
              <div className="flex gap-1">
                {[...Array(4)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-white/30 rounded-full"
                    animate={{
                      height: [8, 16, 8]
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: i * 0.2
                    }}
                  />
                ))}
              </div>
              <span className="text-sm">白噪音 · 深度专注</span>
            </motion.div>
          </>
        ) : (
          /* 完成庆祝界面 */
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="text-center"
          >
            {/* 成就徽章 */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="relative inline-block mb-12"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-[#34C759]/40 to-[#30D158]/40 rounded-full blur-3xl" />
              <div className="relative w-32 h-32 rounded-full bg-gradient-to-br from-[#34C759] to-[#30D158] flex items-center justify-center"
                style={{ boxShadow: "0 20px 60px rgba(52, 199, 89, 0.4)" }}
              >
                <Check className="w-16 h-16 text-white" strokeWidth={3} />
              </div>
              
              {/* 光线扩散 */}
              {[...Array(8)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-12 bg-gradient-to-t from-[#34C759] to-transparent"
                  style={{
                    left: "50%",
                    top: "50%",
                    transformOrigin: "0 0",
                    transform: `rotate(${i * 45}deg) translate(-50%, -100%)`
                  }}
                  initial={{ opacity: 0, scaleY: 0 }}
                  animate={{ opacity: [0, 0.6, 0], scaleY: [0, 1, 0] }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.1
                  }}
                />
              ))}
            </motion.div>

            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-white mb-4"
            >
              完美的专注时光！
            </motion.h2>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-[#8E8E93] mb-12"
            >
              你刚刚完成了 25 分钟的深度专注<br/>
              这份专注会带来丰硕的成果
            </motion.p>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <Button
                onClick={onExit}
                className="bg-gradient-to-r from-[#34C759] to-[#30D158] hover:shadow-[0_0_40px_rgba(52,199,89,0.4)] text-white px-12 py-7 rounded-full transition-all duration-300"
              >
                返回对话
              </Button>
            </motion.div>
          </motion.div>
        )}

        {/* 退出按钮 */}
        {!isCompleted && (
          <Button
            onClick={onExit}
            variant="ghost"
            className="absolute top-8 right-8 text-white/40 hover:text-white hover:bg-white/5 rounded-full backdrop-blur-xl border border-white/10"
          >
            <X className="w-5 h-5 mr-2" strokeWidth={1.5} />
            提前结束
          </Button>
        )}
      </div>
    </div>
  );
}
