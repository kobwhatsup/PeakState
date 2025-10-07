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
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="fixed bottom-24 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-[#FF5252] to-[#FF8A80] shadow-lg flex items-center justify-center group"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.5, type: "spring", stiffness: 260, damping: 20 }}
    >
      <Heart className="w-6 h-6 text-white" strokeWidth={2.5} fill="white" />

      {/* 提示文字 */}
      <motion.div
        initial={{ opacity: 0, x: 10 }}
        whileHover={{ opacity: 1, x: 0 }}
        className="absolute right-full mr-3 bg-white/10 backdrop-blur-xl rounded-xl px-3 py-2 whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <span className="text-white text-sm font-medium">记录健康数据</span>
      </motion.div>

      {/* 脉冲动画 */}
      <motion.div
        className="absolute inset-0 rounded-full bg-[#FF5252]/30"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.5, 0, 0.5],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </motion.button>
  );
}
