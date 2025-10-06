import { motion } from "motion/react";
import { User } from "lucide-react";

interface CoachAvatarEliteProps {
  type: "wise" | "companion" | "expert";
  size?: "sm" | "md" | "lg" | "xl";
  isActive?: boolean;
}

export function CoachAvatarElite({ type, size = "md", isActive = false }: CoachAvatarEliteProps) {
  const sizeMap = {
    sm: { container: "w-10 h-10", icon: "w-5 h-5" },
    md: { container: "w-14 h-14", icon: "w-7 h-7" },
    lg: { container: "w-20 h-20", icon: "w-10 h-10" },
    xl: { container: "w-28 h-28", icon: "w-14 h-14" }
  };

  const { container, icon } = sizeMap[size];

  // 根据教练类型选择颜色
  const getCoachStyle = () => {
    switch (type) {
      case "wise":
        return {
          background: "linear-gradient(135deg, #B3E5FC 0%, #81D4FA 100%)",
          avatarBg: "#455A64",
          glow: "rgba(77, 208, 225, 0.4)"
        };
      case "companion":
        return {
          background: "linear-gradient(135deg, #80DEEA 0%, #4DD0E1 100%)",
          avatarBg: "#5B7A8C",
          glow: "rgba(77, 208, 225, 0.4)"
        };
      case "expert":
        return {
          background: "linear-gradient(135deg, #CFD8DC 0%, #B0BEC5 100%)",
          avatarBg: "#546E7A",
          glow: "rgba(176, 190, 197, 0.4)"
        };
    }
  };

  const style = getCoachStyle();

  return (
    <div className="relative">
      {/* 激活光晕 */}
      {isActive && (
        <motion.div
          className={`${container} absolute inset-0`}
          style={{
            background: style.glow,
            filter: "blur(12px)",
            borderRadius: "50%"
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0.8, 0.5]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}

      {/* 主头像 */}
      <div
        className={`${container} relative rounded-full flex items-center justify-center`}
        style={{
          background: style.background,
          boxShadow: isActive ? `0 8px 24px ${style.glow}` : "0 4px 12px rgba(0, 0, 0, 0.1)"
        }}
      >
        <div 
          className="w-[70%] h-[70%] rounded-full flex items-center justify-center"
          style={{ background: style.avatarBg }}
        >
          <User className={icon} style={{ color: "rgba(255, 255, 255, 0.9)" }} strokeWidth={1.5} />
        </div>
      </div>
    </div>
  );
}