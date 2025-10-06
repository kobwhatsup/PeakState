import { motion } from "motion/react";

interface CoachAvatarProps {
  type: "wise" | "companion" | "expert";
  size?: "sm" | "md" | "lg" | "xl";
  isActive?: boolean;
}

export function CoachAvatar({ type, size = "md", isActive = false }: CoachAvatarProps) {
  const sizeMap = {
    sm: "w-12 h-12",
    md: "w-16 h-16",
    lg: "w-24 h-24",
    xl: "w-32 h-32"
  };

  const avatarSize = sizeMap[size];

  // 不同教练的颜色主题
  const getCoachColors = () => {
    switch (type) {
      case "wise":
        return {
          primary: "#5E9FE6",
          secondary: "#4A7FBA",
          accent: "#3D6AA0"
        };
      case "companion":
        return {
          primary: "#5FC77A",
          secondary: "#4DA365",
          accent: "#3E864F"
        };
      case "expert":
        return {
          primary: "#A0A0A0",
          secondary: "#808080",
          accent: "#606060"
        };
    }
  };

  const colors = getCoachColors();

  return (
    <motion.div
      className={`${avatarSize} rounded-full relative overflow-hidden`}
      animate={isActive ? {
        scale: [1, 1.05, 1],
      } : {
        scale: [1, 1.02, 1],
      }}
      transition={{
        duration: isActive ? 1.5 : 3,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      style={{
        background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 50%, ${colors.accent} 100%)`
      }}
    >
      {/* 智者 - 眼镜和整洁发型 */}
      {type === "wise" && (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg width="70%" height="70%" viewBox="0 0 100 100" fill="none">
            {/* 头部轮廓 */}
            <ellipse cx="50" cy="55" rx="25" ry="30" fill="rgba(255,255,255,0.2)" />
            {/* 眼镜 */}
            <rect x="25" y="45" width="18" height="12" rx="2" stroke="rgba(255,255,255,0.9)" strokeWidth="2" fill="none" />
            <rect x="57" y="45" width="18" height="12" rx="2" stroke="rgba(255,255,255,0.9)" strokeWidth="2" fill="none" />
            <line x1="43" y1="51" x2="57" y2="51" stroke="rgba(255,255,255,0.9)" strokeWidth="2" />
            {/* 发型 */}
            <path d="M 30 35 Q 50 25 70 35" stroke="rgba(255,255,255,0.3)" strokeWidth="3" fill="none" />
          </svg>
        </div>
      )}

      {/* 伙伴 - 微笑和开放姿态 */}
      {type === "companion" && (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg width="70%" height="70%" viewBox="0 0 100 100" fill="none">
            {/* ��部轮廓 */}
            <circle cx="50" cy="50" r="28" fill="rgba(255,255,255,0.2)" />
            {/* 眼睛 */}
            <circle cx="40" cy="45" r="3" fill="rgba(255,255,255,0.9)" />
            <circle cx="60" cy="45" r="3" fill="rgba(255,255,255,0.9)" />
            {/* 微笑 */}
            <path d="M 35 58 Q 50 68 65 58" stroke="rgba(255,255,255,0.9)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
          </svg>
        </div>
      )}

      {/* 专家 - 简约侧脸剪影 */}
      {type === "expert" && (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg width="70%" height="70%" viewBox="0 0 100 100" fill="none">
            {/* 侧脸剪影 */}
            <path 
              d="M 45 25 Q 55 20 60 25 L 65 35 Q 68 45 65 55 L 60 70 Q 55 75 50 75 L 45 70 Q 40 60 42 50 L 45 35 Z" 
              fill="rgba(255,255,255,0.25)" 
            />
            <path 
              d="M 60 35 Q 65 35 65 40" 
              stroke="rgba(255,255,255,0.4)" 
              strokeWidth="1.5" 
              fill="none" 
            />
          </svg>
        </div>
      )}

      {/* 呼吸光晕效果 */}
      <motion.div
        className="absolute inset-0 rounded-full"
        animate={{
          boxShadow: isActive 
            ? [`0 0 20px ${colors.primary}80`, `0 0 30px ${colors.primary}60`, `0 0 20px ${colors.primary}80`]
            : [`0 0 10px ${colors.primary}40`, `0 0 15px ${colors.primary}30`, `0 0 10px ${colors.primary}40`]
        }}
        transition={{
          duration: isActive ? 1.5 : 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </motion.div>
  );
}
