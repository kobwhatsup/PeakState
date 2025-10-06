import { motion } from "motion/react";

interface CoachAvatarPremiumProps {
  type: "wise" | "companion" | "expert";
  size?: "sm" | "md" | "lg" | "xl";
  isActive?: boolean;
}

export function CoachAvatarPremium({ type, size = "md", isActive = false }: CoachAvatarPremiumProps) {
  const sizeMap = {
    sm: { container: "w-14 h-14", icon: 32 },
    md: { container: "w-20 h-20", icon: 48 },
    lg: { container: "w-28 h-28", icon: 64 },
    xl: { container: "w-40 h-40", icon: 96 }
  };

  const { container, icon } = sizeMap[size];

  // 高级渐变配色
  const getCoachTheme = () => {
    switch (type) {
      case "wise":
        return {
          gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          glow: "rgba(102, 126, 234, 0.4)",
          particles: "#a78bfa"
        };
      case "companion":
        return {
          gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
          glow: "rgba(240, 147, 251, 0.4)",
          particles: "#fbbf24"
        };
      case "expert":
        return {
          gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
          glow: "rgba(79, 172, 254, 0.4)",
          particles: "#60a5fa"
        };
    }
  };

  const theme = getCoachTheme();

  return (
    <div className="relative">
      {/* 外层光晕 */}
      <motion.div
        className={`${container} absolute inset-0`}
        animate={{
          opacity: isActive ? [0.3, 0.6, 0.3] : [0.2, 0.4, 0.2],
          scale: isActive ? [1, 1.3, 1] : [1, 1.2, 1]
        }}
        transition={{
          duration: isActive ? 2 : 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        style={{
          background: theme.glow,
          filter: "blur(20px)",
          borderRadius: "50%"
        }}
      />

      {/* 主体头像 */}
      <motion.div
        className={`${container} relative rounded-full overflow-hidden backdrop-blur-xl`}
        style={{
          background: theme.gradient,
          boxShadow: `0 8px 32px ${theme.glow}, inset 0 1px 1px rgba(255,255,255,0.1)`
        }}
        animate={{
          scale: isActive ? [1, 1.05, 1] : [1, 1.02, 1]
        }}
        transition={{
          duration: isActive ? 1.5 : 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {/* 内部光效 - 静态版 */}
        <div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2) 0%, transparent 60%)`
          }}
        />

        {/* 抽象图形 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <svg width={icon} height={icon} viewBox="0 0 100 100" fill="none">
            {type === "wise" && (
              <g>
                {/* 智慧之眼 - 简化版 */}
                <circle
                  cx="50"
                  cy="50"
                  r="25"
                  stroke="rgba(255,255,255,0.6)"
                  strokeWidth="2"
                  fill="none"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="15"
                  stroke="rgba(255,255,255,0.4)"
                  strokeWidth="2"
                  fill="none"
                />
                <circle cx="50" cy="50" r="6" fill="rgba(255,255,255,0.8)" />
                {/* 简化光线 */}
                {[0, 90, 180, 270].map((angle, i) => (
                  <line
                    key={i}
                    x1="50"
                    y1="50"
                    x2={50 + Math.cos((angle * Math.PI) / 180) * 35}
                    y2={50 + Math.sin((angle * Math.PI) / 180) * 35}
                    stroke="rgba(255,255,255,0.4)"
                    strokeWidth="1"
                  />
                ))}
              </g>
            )}

            {type === "companion" && (
              <g>
                {/* 心形 - 静态版 */}
                <path
                  d="M50,35 C50,30 45,25 40,25 C30,25 30,35 30,40 C30,50 50,65 50,65 C50,65 70,50 70,40 C70,35 70,25 60,25 C55,25 50,30 50,35 Z"
                  fill="rgba(255,255,255,0.2)"
                  stroke="rgba(255,255,255,0.6)"
                  strokeWidth="2"
                />
                {/* 简化波纹 */}
                <circle
                  cx="50"
                  cy="45"
                  r="20"
                  stroke="rgba(255,255,255,0.3)"
                  strokeWidth="1.5"
                  fill="none"
                />
              </g>
            )}

            {type === "expert" && (
              <g>
                {/* 精准网格 - 静态版 */}
                <rect
                  x="25"
                  y="25"
                  width="50"
                  height="50"
                  stroke="rgba(255,255,255,0.5)"
                  strokeWidth="2"
                  fill="none"
                  rx="5"
                />
                <rect
                  x="35"
                  y="35"
                  width="30"
                  height="30"
                  stroke="rgba(255,255,255,0.4)"
                  strokeWidth="2"
                  fill="none"
                  rx="3"
                />
                {/* 数据点 */}
                {[
                  [35, 35], [65, 35], [35, 65], [65, 65], [50, 50]
                ].map(([x, y], i) => (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r="3"
                    fill="rgba(255,255,255,0.7)"
                  />
                ))}
              </g>
            )}
          </svg>
        </div>

        {/* 粒子效果 - 简化版 */}
        {isActive && (
          <>
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full"
                style={{ backgroundColor: theme.particles }}
                initial={{
                  x: "50%",
                  y: "50%",
                  opacity: 0
                }}
                animate={{
                  x: `${50 + Math.cos((i * 120 * Math.PI) / 180) * 100}%`,
                  y: `${50 + Math.sin((i * 120 * Math.PI) / 180) * 100}%`,
                  opacity: [0, 1, 0]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.4
                }}
              />
            ))}
          </>
        )}

        {/* 边缘高光 */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{
            background: "linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 50%, rgba(255,255,255,0.1) 100%)"
          }}
        />
      </motion.div>
    </div>
  );
}
