import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Pause, Play, Check } from "lucide-react";
import { Button } from "./ui/button";

interface FocusModeEliteProps {
  onExit: () => void;
}

export function FocusModeElite({ onExit }: FocusModeEliteProps) {
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

  return (
    <div className="min-h-full relative overflow-hidden flex items-center justify-center">
      {/* 柔和背景 */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0"
          style={{
            background: "radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 60%)"
          }}
        />
      </div>

      {/* 主内容 */}
      <div className="relative z-10 text-center px-4 sm:px-5 lg:px-6 max-w-2xl w-full">
        {!isCompleted ? (
          <>
            {/* 关闭按钮 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-4 right-4 sm:top-6 sm:right-6 lg:top-8 lg:right-8"
            >
              <Button
                onClick={onExit}
                variant="ghost"
                size="icon"
                className="touch-target w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-xl border border-white/20 text-white transition-all"
              >
                <X className="w-5 h-5 sm:w-6 sm:h-6" strokeWidth={1.5} />
              </Button>
            </motion.div>

            {/* 计时器环 */}
            <div className="relative mb-12 sm:mb-16 lg:mb-20 mx-auto scale-75 sm:scale-90 lg:scale-100">
              {/* 外层光环 */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-[400px] h-[400px] rounded-full bg-gradient-to-br from-white/10 to-[#4DD0E1]/10 blur-3xl opacity-40" />
              </div>

              {/* 进度环 */}
              <svg className="w-[360px] h-[360px] transform -rotate-90 relative">
                {/* 背景环 */}
                <circle
                  cx="180"
                  cy="180"
                  r="150"
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.1)"
                  strokeWidth="12"
                />

                {/* 进度环 */}
                <circle
                  cx="180"
                  cy="180"
                  r="150"
                  fill="none"
                  stroke="url(#focusGradient)"
                  strokeWidth="12"
                  strokeDasharray="942"
                  strokeDashoffset={942 - (942 * progress) / 100}
                  strokeLinecap="round"
                  style={{
                    filter: "drop-shadow(0 0 8px rgba(77, 208, 225, 0.5))",
                    transition: "stroke-dashoffset 1s linear"
                  }}
                />

                <defs>
                  <linearGradient id="focusGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#4DD0E1" />
                    <stop offset="50%" stopColor="#80DEEA" />
                    <stop offset="100%" stopColor="#B3E5FC" />
                  </linearGradient>
                </defs>
              </svg>

              {/* 中心时间显示 */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div
                    className="text-white mb-4 sm:mb-6 lg:mb-8"
                    style={{
                      fontSize: 'clamp(3rem, 12vw, 5rem)',
                      lineHeight: 1,
                      fontVariantNumeric: 'tabular-nums',
                      fontWeight: 300,
                      letterSpacing: '0.05em'
                    }}
                  >
                    <span>{time.minutes}</span>
                    <span className="opacity-40 mx-1 sm:mx-2">:</span>
                    <span>{time.seconds}</span>
                  </div>

                  <p className="text-white/90 text-base sm:text-lg">
                    {isActive ? "保持专注" : "已暂停"}
                  </p>
                </div>
              </div>
            </div>

            {/* 控制按钮 */}
            <div className="flex items-center justify-center gap-6 sm:gap-8">
              <Button
                onClick={() => setIsActive(!isActive)}
                variant="ghost"
                size="lg"
                className="touch-target w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-white/15 hover:bg-white/25 backdrop-blur-xl border border-white/30 hover:border-white/40 transition-all"
              >
                {isActive ? (
                  <Pause className="w-6 h-6 sm:w-7 sm:h-7 text-white" strokeWidth={1.5} />
                ) : (
                  <Play className="w-6 h-6 sm:w-7 sm:h-7 text-white" strokeWidth={1.5} />
                )}
              </Button>

              <Button
                onClick={onExit}
                variant="ghost"
                size="lg"
                className="touch-target w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-white/15 hover:bg-white/25 backdrop-blur-xl border border-white/30 hover:border-white/40 transition-all"
              >
                <X className="w-6 h-6 sm:w-7 sm:h-7 text-white" strokeWidth={1.5} />
              </Button>
            </div>
          </>
        ) : (
          /* 完成状态 */
          <AnimatePresence>
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              >
                <div
                  className="w-24 h-24 sm:w-28 sm:h-28 lg:w-32 lg:h-32 rounded-full mx-auto mb-8 sm:mb-9 lg:mb-10 flex items-center justify-center"
                  style={{
                    background: "rgba(77, 208, 225, 0.3)",
                    backdropFilter: "blur(10px)",
                    boxShadow: "0 20px 60px rgba(77, 208, 225, 0.3)"
                  }}
                >
                  <Check className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 text-white" strokeWidth={1.5} />
                </div>
              </motion.div>

              <h2 className="text-white mb-4 sm:mb-5 lg:mb-6 text-xl sm:text-2xl">专注时段完成</h2>
              <p className="text-white/80 text-base sm:text-lg mb-8 sm:mb-10 lg:mb-12 leading-relaxed">
                恭喜！您已完成 25 分钟的专注时段
              </p>

              <Button
                onClick={onExit}
                className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-8 py-5 sm:px-10 sm:py-6 lg:px-12 lg:py-7 rounded-2xl shadow-lg shadow-black/10 hover:shadow-xl hover:shadow-black/15 transition-all duration-300 text-base sm:text-lg"
              >
                返回对话
              </Button>
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}