import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { X, Pause, Play } from "lucide-react";
import { Button } from "./ui/button";

interface FocusModeProps {
  onExit: () => void;
}

export function FocusMode({ onExit }: FocusModeProps) {
  const [duration] = useState(25 * 60); // 25分钟专注时间
  const [timeLeft, setTimeLeft] = useState(duration);
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => time - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      // 时间到了
      setIsActive(false);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeLeft]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const progress = ((duration - timeLeft) / duration) * 100;

  // 渐变背景色彩从蓝色到绿色
  const getGradientColor = () => {
    const blueAmount = Math.max(0, 100 - progress);
    const greenAmount = Math.min(100, progress);
    return {
      from: `rgba(10, 132, 255, ${0.2 + blueAmount / 500})`,
      to: `rgba(52, 199, 89, ${0.2 + greenAmount / 500})`
    };
  };

  const gradient = getGradientColor();

  return (
    <div className="min-h-screen bg-[#1C1C1E] relative overflow-hidden flex items-center justify-center">
      {/* 动态背景 */}
      <motion.div
        className="absolute inset-0"
        animate={{
          background: [
            `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
            `linear-gradient(145deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
            `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
          ]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* 模糊色块装饰 */}
      <motion.div
        className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full"
        style={{
          background: "rgba(10, 132, 255, 0.15)",
          filter: "blur(80px)"
        }}
        animate={{
          x: [0, 50, 0],
          y: [0, 30, 0],
          scale: [1, 1.2, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <motion.div
        className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full"
        style={{
          background: "rgba(52, 199, 89, 0.15)",
          filter: "blur(80px)"
        }}
        animate={{
          x: [0, -50, 0],
          y: [0, -30, 0],
          scale: [1, 1.3, 1]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
      />

      {/* 内容 */}
      <div className="relative z-10 text-center px-6">
        {/* 圆形进度环 */}
        <div className="relative mb-12 mx-auto w-80 h-80">
          <svg className="w-full h-full transform -rotate-90">
            {/* 背景圆环 */}
            <circle
              cx="160"
              cy="160"
              r="140"
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="4"
              fill="none"
            />
            {/* 进度圆环 */}
            <motion.circle
              cx="160"
              cy="160"
              r="140"
              stroke="url(#progressGradient)"
              strokeWidth="4"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 140}
              initial={{ strokeDashoffset: 2 * Math.PI * 140 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 140 * (1 - progress / 100) }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0A84FF" />
                <stop offset="100%" stopColor="#34C759" />
              </linearGradient>
            </defs>
          </svg>

          {/* 时间显示 */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.div
              key={timeLeft}
              initial={{ scale: 1.1, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-white mb-4" style={{ fontSize: '5rem', lineHeight: 1 }}>
                {formatTime(timeLeft)}
              </div>
            </motion.div>
            
            <motion.p
              className="text-white/60"
              animate={{ opacity: [0.6, 1, 0.6] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {timeLeft === 0 ? "完成！" : isActive ? "保持专注" : "已暂停"}
            </motion.p>
          </div>
        </div>

        {/* 控制按钮 */}
        <div className="flex items-center justify-center gap-4">
          <Button
            onClick={() => setIsActive(!isActive)}
            variant="ghost"
            size="lg"
            className="text-white hover:bg-white/10 rounded-full w-16 h-16 p-0"
          >
            {isActive ? (
              <Pause className="w-8 h-8" strokeWidth={1.5} />
            ) : (
              <Play className="w-8 h-8" strokeWidth={1.5} />
            )}
          </Button>
        </div>

        {/* 退出按钮 */}
        <Button
          onClick={onExit}
          variant="ghost"
          className="absolute top-8 right-8 text-white/60 hover:text-white hover:bg-white/10 rounded-full"
        >
          <X className="w-6 h-6 mr-2" strokeWidth={1.5} />
          提前结束
        </Button>

        {/* 呼吸提示 */}
        <motion.div
          className="absolute bottom-12 left-1/2 transform -translate-x-1/2"
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          <p className="text-white/40">深呼吸 · 保持节奏</p>
        </motion.div>
      </div>
    </div>
  );
}
