import { motion } from "motion/react";
import { Brain, Heart, Microscope } from "lucide-react";
import type { CoachType } from "../api";

interface CoachAvatarEliteProps {
  type: CoachType;
  size?: "sm" | "md" | "lg" | "xl";
  isActive?: boolean;
}

export function CoachAvatarElite({ type, size = "md", isActive = false }: CoachAvatarEliteProps) {
  const sizeMap = {
    sm: { container: "w-11 h-11", icon: "w-6 h-6" },
    md: { container: "w-16 h-16", icon: "w-8 h-8" },
    lg: { container: "w-24 h-24", icon: "w-12 h-12" },
    xl: { container: "w-32 h-32", icon: "w-16 h-16" }
  };

  const { container, icon } = sizeMap[size];

  // 根据教练类型选择颜色和图标
  const getCoachStyle = () => {
    switch (type) {
      case "sage":
        return {
          background: "linear-gradient(135deg, #B3E5FC 0%, #81D4FA 100%)",
          avatarBg: "#455A64",
          glow: "rgba(77, 208, 225, 0.5)",
          Icon: Brain
        };
      case "companion":
        return {
          background: "linear-gradient(135deg, #80DEEA 0%, #4DD0E1 100%)",
          avatarBg: "#5B7A8C",
          glow: "rgba(77, 208, 225, 0.5)",
          Icon: Heart
        };
      case "expert":
        return {
          background: "linear-gradient(135deg, #CFD8DC 0%, #B0BEC5 100%)",
          avatarBg: "#546E7A",
          glow: "rgba(176, 190, 197, 0.5)",
          Icon: Microscope
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
            filter: "blur(16px)",
            borderRadius: "50%"
          }}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.6, 0.9, 0.6]
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}

      {/* 主头像 */}
      <div
        className={`${container} relative rounded-full flex items-center justify-center border-2 border-white/30`}
        style={{
          background: style.background,
          boxShadow: isActive ? `0 10px 30px ${style.glow}` : "0 6px 16px rgba(0, 0, 0, 0.15)"
        }}
      >
        <div
          className="w-[72%] h-[72%] rounded-full flex items-center justify-center"
          style={{ background: style.avatarBg }}
        >
          <style.Icon className={icon} style={{ color: "rgba(255, 255, 255, 0.95)" }} strokeWidth={1.8} />
        </div>
      </div>
    </div>
  );
}