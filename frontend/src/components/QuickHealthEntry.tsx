/**
 * 快捷健康数据录入浮动按钮
 * 在聊天界面提供快速录入健康数据的入口
 */

import { motion } from "motion/react";
import { Heart } from "lucide-react";

interface QuickHealthEntryProps {
  onClick: () => void;
}

export function QuickHealthEntry({ onClick }: QuickHealthEntryProps) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      className="fixed bottom-28 right-6 z-50 w-12 h-12 rounded-full bg-gradient-to-br from-[#FF7B9C] to-[#FFA8BB] shadow-xl flex items-center justify-center group"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.5, type: "spring", stiffness: 260, damping: 20 }}
    >
      <Heart className="w-5 h-5 text-white" strokeWidth={2.5} fill="white" />

      {/* 提示文字 */}
      <motion.div
        initial={{ opacity: 0, x: 10 }}
        whileHover={{ opacity: 1, x: 0 }}
        className="absolute right-full mr-3 bg-white/20 backdrop-blur-xl rounded-xl px-3 py-2 whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity border border-white/30"
      >
        <span className="text-white text-sm font-medium">记录健康数据</span>
      </motion.div>

      {/* 脉冲动画 */}
      <motion.div
        className="absolute inset-0 rounded-full bg-[#FF7B9C]/40"
        animate={{
          scale: [1, 1.4, 1],
          opacity: [0.4, 0, 0.4],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </motion.button>
  );
}
