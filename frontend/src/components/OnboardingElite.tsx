import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Activity, Users, TrendingUp, CheckCircle, MessageCircle, Timer, BarChart3, ChevronRight, Shield, CreditCard } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useAuthStore } from "../store/authStore";
import type { CoachType } from "../api";

interface OnboardingEliteProps {
  onComplete: (coachType: CoachType) => void;
}

export function OnboardingElite({ onComplete }: OnboardingEliteProps) {
  // Screen state: 0-7 (8 screens total)
  const [currentScreen, setCurrentScreen] = useState(0);

  // Registration form state
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [selectedCoach, setSelectedCoach] = useState<CoachType>("companion");

  // Quiz state (stored locally before registration)
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(0);

  const { register, isLoading, error } = useAuthStore();

  // Quiz questions for personalization
  const quizQuestions = [
    { id: "sleep", question: "您通常几点入睡？", options: ["22:00前", "22:00-23:00", "23:00-24:00", "24:00后"] },
    { id: "wakeup", question: "您通常几点起床？", options: ["6:00前", "6:00-7:00", "7:00-8:00", "8:00后"] },
    { id: "energy_peak", question: "一天中您精力最充沛的时段？", options: ["早晨", "上午", "下午", "晚上"] },
    { id: "focus_duration", question: "您能持续专注工作的时长？", options: ["<30分钟", "30-60分钟", "1-2小时", ">2小时"] },
    { id: "main_challenge", question: "您最大的精力管理挑战？", options: ["睡眠不足", "拖延症", "注意力分散", "情绪波动"] },
  ];

  return (
    <div className="min-h-full flex items-center justify-center p-4 sm:p-5 lg:p-6 relative overflow-hidden">
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

      {/* Progress indicator */}
      <div className="absolute top-4 sm:top-6 lg:top-8 left-0 right-0 flex justify-center z-20">
        <div className="flex gap-1.5 sm:gap-2">
          {[0, 1, 2, 3, 4, 5, 6, 7].map((index) => (
            <div
              key={index}
              className={`h-1 sm:h-1.5 rounded-full transition-all duration-300 ${
                index === currentScreen
                  ? "w-6 sm:w-8 bg-white"
                  : index < currentScreen
                  ? "w-1 sm:w-1.5 bg-white/60"
                  : "w-1 sm:w-1.5 bg-white/20"
              }`}
            />
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {/* 屏幕 0: 品牌欢迎页 */}
        {currentScreen === 0 && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-lg relative z-10 px-4"
          >
            <motion.div
              className="mb-8 sm:mb-10 lg:mb-12"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <div
                className="w-24 h-24 sm:w-28 sm:h-28 lg:w-32 lg:h-32 rounded-full mx-auto mb-6 sm:mb-7 lg:mb-8"
                style={{
                  background: "linear-gradient(135deg, #B3E5FC 0%, #81D4FA 100%)",
                  boxShadow: "0 20px 60px rgba(77, 208, 225, 0.3)"
                }}
              >
                <div className="w-full h-full rounded-full flex items-center justify-center">
                  <div className="w-24 h-24 rounded-full bg-[#455A64] flex items-center justify-center relative overflow-hidden">
                    <div className="absolute top-6 w-16 h-16 rounded-full bg-[#5B7A8C]" />
                    <div className="absolute bottom-0 w-28 h-20 rounded-t-full bg-[#5B7A8C]" />
                    <div className="absolute top-4 w-12 h-8 rounded-t-full bg-[#37474F]" />
                  </div>
                </div>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4">PeakState</h1>
              <p className="text-white/80 text-base sm:text-lg">您的AI精力管理教练</p>
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <Button
                onClick={() => setCurrentScreen(1)}
                className="w-full max-w-sm bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-8 py-5 sm:px-10 sm:py-6 lg:px-12 lg:py-7 rounded-2xl text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300"
              >
                开始体验
              </Button>
            </motion.div>
          </motion.div>
        )}

        {/* 屏幕 1: 价值主张 1 - 了解自己 */}
        {currentScreen === 1 && (
          <motion.div
            key="value1"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-lg relative z-10 px-4"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full mx-auto mb-6 sm:mb-8 flex items-center justify-center"
                style={{
                  background: "rgba(77, 208, 225, 0.3)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <Activity className="w-10 h-10 sm:w-12 sm:h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">了解你的精力节奏</h2>
            <p className="text-white/80 text-base sm:text-lg mb-8 sm:mb-10 lg:mb-12 leading-relaxed">
              通过科学的数据追踪，发现你独特的精力曲线。
              <br />
              让AI帮你找到最佳状态时刻。
            </p>

            <div className="flex gap-4 justify-center">
              <Button
                onClick={() => setCurrentScreen(2)}
                className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-6 py-4 sm:px-8 sm:py-5 lg:py-6 rounded-2xl transition-all text-base sm:text-lg"
              >
                继续 <ChevronRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* 屏幕 2: 价值主张 2 - AI教练规划 */}
        {currentScreen === 2 && (
          <motion.div
            key="value2"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-lg relative z-10 px-4"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full mx-auto mb-6 sm:mb-8 flex items-center justify-center"
                style={{
                  background: "rgba(91, 159, 219, 0.3)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <Users className="w-10 h-10 sm:w-12 sm:h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">AI教练个性化规划</h2>
            <p className="text-white/80 text-base sm:text-lg mb-8 sm:mb-10 lg:mb-12 leading-relaxed">
              4种AI教练风格，为你量身定制每日计划。
              <br />
              从睡眠、运动到工作，全方位优化你的状态。
            </p>

            <div className="flex gap-4 justify-center">
              <Button
                onClick={() => setCurrentScreen(3)}
                className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-6 py-4 sm:px-8 sm:py-5 lg:py-6 rounded-2xl transition-all text-base sm:text-lg"
              >
                继续 <ChevronRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* 屏幕 3: 价值主张 3 - 数据可视化 */}
        {currentScreen === 3 && (
          <motion.div
            key="value3"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-lg relative z-10 px-4"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full mx-auto mb-6 sm:mb-8 flex items-center justify-center"
                style={{
                  background: "rgba(144, 202, 249, 0.3)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <TrendingUp className="w-10 h-10 sm:w-12 sm:h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">可视化你的进步</h2>
            <p className="text-white/80 text-base sm:text-lg mb-8 sm:mb-10 lg:mb-12 leading-relaxed">
              精美的图表展示你的精力变化趋势。
              <br />
              让每一天的努力都清晰可见。
            </p>

            <div className="flex gap-4 justify-center">
              <Button
                onClick={() => setCurrentScreen(4)}
                className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-6 py-4 sm:px-8 sm:py-5 lg:py-6 rounded-2xl transition-all text-base sm:text-lg"
              >
                试用功能 <ChevronRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* 屏幕 4: 功能体验预览 (核心创新！) */}
        {currentScreen === 4 && (
          <motion.div
            key="trial"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl relative z-10 px-4"
          >
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 sm:mb-3">体验一下？不用注册</h2>
            <p className="text-white/70 text-sm sm:text-base mb-8 sm:mb-10 lg:mb-12">先试用核心功能，再决定是否开始</p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5 lg:gap-6 mb-6 sm:mb-8">
              {/* 聊天体验 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  // TODO: Open trial chat modal
                  alert("试用对话功能 - 将在下个版本实现");
                }}
                className="rounded-2xl sm:rounded-3xl p-6 sm:p-7 lg:p-8 transition-all duration-300 touch-target"
                style={{
                  background: "rgba(77, 208, 225, 0.3)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)"
                }}
              >
                <MessageCircle className="w-10 h-10 sm:w-12 sm:h-12 text-white mx-auto mb-3 sm:mb-4" strokeWidth={1.5} />
                <h3 className="text-white font-semibold mb-1.5 sm:mb-2 text-sm sm:text-base">和AI聊聊</h3>
                <p className="text-white/70 text-xs sm:text-sm">体验AI教练的智能对话</p>
              </motion.button>

              {/* 专注计时体验 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  // TODO: Open trial focus timer
                  alert("试用专注计时 - 将在下个版本实现");
                }}
                className="rounded-2xl sm:rounded-3xl p-6 sm:p-7 lg:p-8 transition-all duration-300 touch-target"
                style={{
                  background: "rgba(91, 159, 219, 0.3)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)"
                }}
              >
                <Timer className="w-10 h-10 sm:w-12 sm:h-12 text-white mx-auto mb-3 sm:mb-4" strokeWidth={1.5} />
                <h3 className="text-white font-semibold mb-1.5 sm:mb-2 text-sm sm:text-base">体验专注计时</h3>
                <p className="text-white/70 text-xs sm:text-sm">尝试我们的番茄钟功能</p>
              </motion.button>

              {/* 报告示例 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  // TODO: Open sample report
                  alert("查看报告示例 - 将在下个版本实现");
                }}
                className="rounded-2xl sm:rounded-3xl p-6 sm:p-7 lg:p-8 transition-all duration-300 touch-target"
                style={{
                  background: "rgba(144, 202, 249, 0.3)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)"
                }}
              >
                <BarChart3 className="w-10 h-10 sm:w-12 sm:h-12 text-white mx-auto mb-3 sm:mb-4" strokeWidth={1.5} />
                <h3 className="text-white font-semibold mb-1.5 sm:mb-2 text-sm sm:text-base">查看精力报告示例</h3>
                <p className="text-white/70 text-xs sm:text-sm">浏览Demo数据可视化</p>
              </motion.button>
            </div>

            <Button
              onClick={() => setCurrentScreen(5)}
              className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-8 py-4 sm:px-10 sm:py-5 lg:px-12 lg:py-6 rounded-2xl transition-all text-base sm:text-lg"
            >
              继续了解 <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        )}

        {/* 屏幕 5: 选择AI教练 */}
        {currentScreen === 5 && (
          <motion.div
            key="coach-selection"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl relative z-10 px-4"
          >
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 sm:mb-3">选择您的能量管理师风格</h2>
            <p className="text-white/70 text-sm sm:text-base mb-8 sm:mb-10 lg:mb-12">三位能量管理师，不同的偏好和特长</p>

            <div className="grid grid-cols-3 gap-3 sm:gap-4 lg:gap-6 mb-6 sm:mb-8">
              {[
                { type: "sage" as CoachType, label: "温言", desc: "温和睿智，启发式引导", emoji: "🌟" },
                { type: "companion" as CoachType, label: "明亮", desc: "亲切自然，温暖陪伴", emoji: "☀️" },
                { type: "expert" as CoachType, label: "深思", desc: "理性分析，洞察本质", emoji: "🔍" },
              ].map((coach) => (
                <motion.button
                  key={coach.type}
                  type="button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedCoach(coach.type)}
                  className={`rounded-2xl sm:rounded-3xl p-4 sm:p-5 lg:p-6 transition-all duration-300 touch-target ${
                    selectedCoach === coach.type
                      ? "bg-white/40 border-2 border-white/80"
                      : "bg-white/20 border-2 border-white/30"
                  }`}
                  style={{ backdropFilter: "blur(10px)" }}
                >
                  <div className="text-3xl sm:text-4xl mb-2 sm:mb-3">{coach.emoji}</div>
                  <div className="text-white font-semibold mb-1 text-sm sm:text-base">{coach.label}</div>
                  <div className="text-white/70 text-xs leading-tight">{coach.desc}</div>
                </motion.button>
              ))}
            </div>

            <Button
              onClick={() => setCurrentScreen(6)}
              disabled={!selectedCoach}
              className="bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-8 py-4 sm:px-10 sm:py-5 lg:px-12 lg:py-6 rounded-2xl transition-all disabled:opacity-50 text-base sm:text-lg"
            >
              下一步 <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        )}

        {/* 屏幕 6: 个性化问卷 */}
        {currentScreen === 6 && (
          <motion.div
            key="quiz"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl relative z-10 px-4"
          >
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-2 sm:mb-3">
              {quizQuestions[currentQuizQuestion].question}
            </h2>
            <p className="text-white/70 text-sm sm:text-base mb-8 sm:mb-10 lg:mb-12">
              问题 {currentQuizQuestion + 1} / {quizQuestions.length}
            </p>

            <div className="grid grid-cols-1 gap-3 sm:gap-4 mb-6 sm:mb-8 max-w-md mx-auto">
              {quizQuestions[currentQuizQuestion].options.map((option) => (
                <motion.button
                  key={option}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setQuizAnswers({
                      ...quizAnswers,
                      [quizQuestions[currentQuizQuestion].id]: option,
                    });

                    if (currentQuizQuestion < quizQuestions.length - 1) {
                      setCurrentQuizQuestion(currentQuizQuestion + 1);
                    } else {
                      // Quiz complete, move to registration
                      setCurrentScreen(7);
                    }
                  }}
                  className="rounded-2xl p-4 sm:p-5 lg:p-6 text-white text-base sm:text-lg transition-all duration-300 hover:bg-white/30 touch-target"
                  style={{
                    background: "rgba(255, 255, 255, 0.2)",
                    backdropFilter: "blur(10px)",
                    border: "1px solid rgba(255, 255, 255, 0.3)"
                  }}
                >
                  {option}
                </motion.button>
              ))}
            </div>

            <button
              onClick={() => setCurrentScreen(7)}
              className="text-white/60 hover:text-white/80 text-sm transition-colors"
            >
              跳过问卷
            </button>
          </motion.div>
        )}

        {/* 屏幕 7: 注册 + 数据授权 */}
        {currentScreen === 7 && (
          <motion.div
            key="registration"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center max-w-md relative z-10 px-4"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full mx-auto mb-6 sm:mb-8 flex items-center justify-center"
                style={{
                  background: "rgba(77, 208, 225, 0.3)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <CheckCircle className="w-10 h-10 sm:w-12 sm:h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">创建您的账号</h2>
            <p className="text-white/80 text-sm sm:text-base mb-6 sm:mb-8 leading-relaxed">
              开始您的精力管理之旅
            </p>

            {/* 注册表单 */}
            <div className="w-full space-y-5 sm:space-y-6">
              <div className="space-y-3 sm:space-y-4">
                <Input
                  type="tel"
                  placeholder="手机号码"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-4 py-4 sm:px-5 sm:py-5 lg:px-6 lg:py-6 text-base"
                />
                <Input
                  type="password"
                  placeholder="设置密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-4 py-4 sm:px-5 sm:py-5 lg:px-6 lg:py-6 text-base"
                />
                <Input
                  type="password"
                  placeholder="确认密码"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-4 py-4 sm:px-5 sm:py-5 lg:px-6 lg:py-6 text-base"
                />
              </div>

              {/* 数据授权说明 */}
              <div className="rounded-2xl p-4 bg-white/10 backdrop-blur-xl border border-white/20">
                <div className="flex items-start gap-3 text-left">
                  <Shield className="w-5 h-5 text-white/80 flex-shrink-0 mt-0.5" />
                  <div className="text-white/80 text-sm">
                    <p className="mb-2">为了提供个性化建议，我们需要访问：</p>
                    <ul className="text-xs space-y-1 text-white/60">
                      <li>• 健康数据（可选）- 睡眠、运动、心率</li>
                      <li>• 日历数据（可选）- 优化时间安排</li>
                      <li>• 通知权限 - 及时提醒</li>
                    </ul>
                    <p className="text-xs mt-2">所有数据均加密存储，您可随时撤销授权</p>
                  </div>
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
                    // TODO: Upload quiz answers after successful registration
                    console.log("Quiz answers to upload:", quizAnswers);
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
                className="w-full bg-white/90 hover:bg-white text-[#2B69B6] touch-target px-8 py-5 sm:px-10 sm:py-6 lg:px-12 lg:py-7 rounded-2xl shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-base sm:text-lg"
              >
                {isLoading ? "注册中..." : "创建账号"}
              </Button>

              <p className="text-white/60 text-xs">
                注册即表示同意
                <button className="text-white/80 underline ml-1">用户协议</button>和
                <button className="text-white/80 underline ml-1">隐私政策</button>
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
