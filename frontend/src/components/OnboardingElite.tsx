import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Activity, Users, TrendingUp, CheckCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useAuthStore } from "../store/authStore";
import type { CoachType } from "../api";

interface OnboardingEliteProps {
  onComplete: (coachType: CoachType) => void;
}

export function OnboardingElite({ onComplete }: OnboardingEliteProps) {
  const [currentScreen, setCurrentScreen] = useState(0);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [selectedCoach, setSelectedCoach] = useState<CoachType>("coach");

  const { register, isLoading, error } = useAuthStore();

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      {/* 柔和的圆形背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-[800px] h-[800px] rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 60%)",
            top: "-20%",
            left: "50%",
            transform: "translateX(-50%)",
            filter: "blur(100px)"
          }}
        />
        <div
          className="absolute w-[600px] h-[600px] rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(77, 208, 225, 0.1) 0%, transparent 70%)",
            bottom: "-10%",
            left: "-10%",
            filter: "blur(80px)"
          }}
        />
      </div>

      <AnimatePresence mode="wait">
        {/* 欢迎页 */}
        {currentScreen === 0 && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-lg relative z-10"
          >
            {/* 用户头像 */}
            <motion.div
              className="mb-12"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <div 
                className="w-32 h-32 rounded-full mx-auto mb-8"
                style={{
                  background: "linear-gradient(135deg, #B3E5FC 0%, #81D4FA 100%)",
                  boxShadow: "0 20px 60px rgba(77, 208, 225, 0.3)"
                }}
              >
                <div className="w-full h-full rounded-full flex items-center justify-center">
                  <div className="w-24 h-24 rounded-full bg-[#455A64] flex items-center justify-center relative overflow-hidden">
                    {/* 简单的头像图形 */}
                    <div className="absolute top-6 w-16 h-16 rounded-full bg-[#5B7A8C]" />
                    <div className="absolute bottom-0 w-28 h-20 rounded-t-full bg-[#5B7A8C]" />
                    <div className="absolute top-4 w-12 h-8 rounded-t-full bg-[#37474F]" />
                  </div>
                </div>
              </div>

              <h1 className="text-white mb-4">Welcome [User]</h1>
              <p className="text-white/80 text-lg">Your Energy Coach</p>
            </motion.div>

            {/* 进度圆环预览 */}
            <motion.div
              className="mb-16"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <svg className="w-64 h-64 mx-auto transform -rotate-90">
                <circle
                  cx="128"
                  cy="128"
                  r="100"
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.1)"
                  strokeWidth="20"
                />
                <circle
                  cx="128"
                  cy="128"
                  r="100"
                  fill="none"
                  stroke="url(#gradient1)"
                  strokeWidth="20"
                  strokeDasharray="628"
                  strokeDashoffset="200"
                  strokeLinecap="round"
                  style={{ filter: "drop-shadow(0 0 8px rgba(77, 208, 225, 0.5))" }}
                />
                <circle
                  cx="128"
                  cy="128"
                  r="100"
                  fill="none"
                  stroke="url(#gradient2)"
                  strokeWidth="20"
                  strokeDasharray="628"
                  strokeDashoffset="420"
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#4DD0E1" />
                    <stop offset="100%" stopColor="#80DEEA" />
                  </linearGradient>
                  <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#5B9FDB" />
                    <stop offset="100%" stopColor="#4A8DCF" />
                  </linearGradient>
                </defs>
              </svg>
            </motion.div>

            {/* 底部操作卡片 */}
            <motion.div
              className="grid grid-cols-3 gap-4"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <button
                onClick={() => setCurrentScreen(1)}
                className="aspect-square rounded-3xl p-6 flex flex-col items-center justify-center transition-all duration-300 hover:scale-105"
                style={{
                  background: "rgba(144, 202, 249, 0.4)",
                  backdropFilter: "blur(10px)",
                  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
                }}
              >
                <Activity className="w-8 h-8 text-[#1E3A8A] mb-3" strokeWidth={1.5} />
                <span className="text-sm text-[#1E3A8A]">Energy Check-in</span>
              </button>

              <button
                onClick={() => setCurrentScreen(1)}
                className="aspect-square rounded-3xl p-6 flex flex-col items-center justify-center transition-all duration-300 hover:scale-105"
                style={{
                  background: "rgba(77, 208, 225, 0.5)",
                  backdropFilter: "blur(10px)",
                  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
                }}
              >
                <Users className="w-8 h-8 text-[#1E3A8A] mb-3" strokeWidth={1.5} />
                <span className="text-sm text-[#1E3A8A]">Daily Plan</span>
              </button>

              <button
                onClick={() => setCurrentScreen(1)}
                className="aspect-square rounded-3xl p-6 flex flex-col items-center justify-center transition-all duration-300 hover:scale-105"
                style={{
                  background: "rgba(200, 210, 220, 0.4)",
                  backdropFilter: "blur(10px)",
                  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
                }}
              >
                <TrendingUp className="w-8 h-8 text-[#546E7A] mb-3" strokeWidth={1.5} />
                <span className="text-sm text-[#546E7A]">Insights</span>
              </button>
            </motion.div>
          </motion.div>
        )}

        {/* 完成页 */}
        {currentScreen === 1 && (
          <motion.div
            key="complete"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center max-w-md relative z-10"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              <div className="w-24 h-24 rounded-full mx-auto mb-8 flex items-center justify-center"
                style={{
                  background: "rgba(77, 208, 225, 0.3)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <CheckCircle className="w-12 h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>

            <h2 className="text-white mb-4">准备就绪</h2>
            <p className="text-white/80 mb-12 leading-relaxed">
              开始您的精力管理之旅
            </p>

            {/* 注册表单 */}
            <div className="w-full max-w-sm space-y-6">
              <div className="space-y-4">
                <Input
                  type="tel"
                  placeholder="手机号码"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-6 py-6"
                />
                <Input
                  type="password"
                  placeholder="设置密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-6 py-6"
                />
                <Input
                  type="password"
                  placeholder="确认密码"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-6 py-6"
                />
              </div>

              {/* 选择教练类型 */}
              <div className="space-y-3">
                <p className="text-white/80 text-sm text-center">选择您的AI教练</p>
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { type: "mentor" as CoachType, label: "导师" },
                    { type: "coach" as CoachType, label: "教练" },
                    { type: "doctor" as CoachType, label: "医生" },
                    { type: "zen" as CoachType, label: "禅师" },
                  ].map((coach) => (
                    <button
                      key={coach.type}
                      type="button"
                      onClick={() => setSelectedCoach(coach.type)}
                      className={`rounded-2xl p-4 transition-all duration-300 hover:scale-105 ${
                        selectedCoach === coach.type
                          ? "bg-white/30 border-2 border-white/60"
                          : "bg-white/15 border-2 border-white/20 hover:bg-white/20"
                      }`}
                    >
                      <span className="text-white text-sm font-medium">{coach.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <p className="text-red-300 text-sm text-center">{error}</p>
              )}

              <Button
                onClick={async () => {
                  if (!phoneNumber || !password || !confirmPassword) {
                    return;
                  }
                  if (password !== confirmPassword) {
                    return;
                  }
                  try {
                    await register({
                      phone_number: phoneNumber,
                      password,
                      coach_selection: selectedCoach,
                    });
                    onComplete(selectedCoach);
                  } catch (err) {
                    console.error("Registration failed:", err);
                  }
                }}
                disabled={
                  isLoading ||
                  !phoneNumber ||
                  !password ||
                  !confirmPassword ||
                  password !== confirmPassword
                }
                className="w-full bg-white/90 hover:bg-white text-[#2B69B6] px-12 py-7 rounded-2xl shadow-lg shadow-black/10 hover:shadow-xl hover:shadow-black/15 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? "注册中..." : "立即开始"}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}