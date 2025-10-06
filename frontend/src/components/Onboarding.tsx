import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Brain, Heart, MessageCircle, Calendar, ChevronRight } from "lucide-react";
import { Button } from "./ui/button";
import { CoachAvatar } from "./CoachAvatar";

interface OnboardingProps {
  onComplete: (coachType: "wise" | "companion" | "expert") => void;
}

export function Onboarding({ onComplete }: OnboardingProps) {
  const [currentScreen, setCurrentScreen] = useState(0);
  const [selectedCoach, setSelectedCoach] = useState<"wise" | "companion" | "expert" | null>(null);

  const nextScreen = () => {
    if (currentScreen < 4) {
      setCurrentScreen(currentScreen + 1);
    } else if (selectedCoach) {
      onComplete(selectedCoach);
    }
  };

  const selectCoach = (type: "wise" | "companion" | "expert") => {
    setSelectedCoach(type);
    setTimeout(() => nextScreen(), 1000);
  };

  const coaches = [
    { type: "wise" as const, name: "智者", description: "冷静专业，深度分析" },
    { type: "companion" as const, name: "伙伴", description: "温暖陪伴，积极鼓励" },
    { type: "expert" as const, name: "专家", description: "简洁高效，精准指导" }
  ];

  return (
    <div className="min-h-screen bg-[#1C1C1E] flex items-center justify-center p-6">
      <AnimatePresence mode="wait">
        {/* Screen 1: 欢迎页 */}
        {currentScreen === 0 && (
          <motion.div
            key="screen-0"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md"
          >
            <motion.div
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              className="mb-12"
            >
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-[#0A84FF] to-[#5E9FE6] flex items-center justify-center">
                <Brain className="w-12 h-12 text-white" strokeWidth={1.5} />
              </div>
            </motion.div>
            
            <h1 className="mb-4 text-white opacity-90">你好，未来的自己。</h1>
            <p className="text-[#8E8E93] mb-12">开启智能精力管理的旅程</p>
            
            <Button 
              onClick={nextScreen}
              className="bg-[#0A84FF] hover:bg-[#0A84FF]/90 text-white px-8 py-6 rounded-full"
            >
              开始
              <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        )}

        {/* Screen 2: 价值呈现1 */}
        {currentScreen === 1 && (
          <motion.div
            key="screen-1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md"
          >
            <div className="mb-12 flex justify-center gap-8">
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <Brain className="w-16 h-16 text-[#0A84FF]" strokeWidth={1.5} />
              </motion.div>
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
              >
                <Heart className="w-16 h-16 text-[#FF375F]" strokeWidth={1.5} />
              </motion.div>
            </div>
            
            <h2 className="mb-4 text-white">整合生理与心理数据</h2>
            <p className="text-[#8E8E93] mb-12">认识真实的你</p>
            
            <Button 
              onClick={nextScreen}
              className="bg-[#0A84FF] hover:bg-[#0A84FF]/90 text-white px-8 py-6 rounded-full"
            >
              继续
              <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        )}

        {/* Screen 3: 价值呈现2 */}
        {currentScreen === 2 && (
          <motion.div
            key="screen-2"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md"
          >
            <div className="mb-12 flex justify-center gap-8">
              <motion.div
                animate={{ rotate: [0, 5, 0, -5, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <MessageCircle className="w-16 h-16 text-[#34C759]" strokeWidth={1.5} />
              </motion.div>
              <motion.div
                animate={{ rotate: [0, -5, 0, 5, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
              >
                <Calendar className="w-16 h-16 text-[#FF9500]" strokeWidth={1.5} />
              </motion.div>
            </div>
            
            <h2 className="mb-4 text-white">AI教练主动规划</h2>
            <p className="text-[#8E8E93] mb-12">让精力用在刀刃上</p>
            
            <Button 
              onClick={nextScreen}
              className="bg-[#0A84FF] hover:bg-[#0A84FF]/90 text-white px-8 py-6 rounded-full"
            >
              继续
              <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        )}

        {/* Screen 4: 教练选择 */}
        {currentScreen === 3 && (
          <motion.div
            key="screen-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md w-full"
          >
            <h2 className="mb-3 text-white">选择你的AI教练</h2>
            <p className="text-[#8E8E93] mb-12">每位教练都有独特的风格</p>
            
            <div className="space-y-4 mb-8">
              {coaches.map((coach) => (
                <motion.button
                  key={coach.type}
                  onClick={() => selectCoach(coach.type)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full bg-[#2C2C2E] hover:bg-[#3C3C3E] rounded-2xl p-6 flex items-center gap-4 transition-colors ${
                    selectedCoach === coach.type ? 'ring-2 ring-[#0A84FF]' : ''
                  }`}
                >
                  <CoachAvatar type={coach.type} size="lg" isActive={selectedCoach === coach.type} />
                  <div className="flex-1 text-left">
                    <h3 className="text-white mb-1">{coach.name}</h3>
                    <p className="text-[#8E8E93]">{coach.description}</p>
                  </div>
                  {selectedCoach === coach.type && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 rounded-full bg-[#0A84FF] flex items-center justify-center"
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </motion.div>
                  )}
                </motion.button>
              ))}
            </div>

            <AnimatePresence>
              {selectedCoach && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="bg-[#2C2C2E] rounded-2xl p-6"
                >
                  <div className="flex items-start gap-3">
                    <CoachAvatar type={selectedCoach} size="sm" isActive />
                    <div className="flex-1 text-left">
                      <p className="text-white">你好，我是你的AI教练。</p>
                      <p className="text-white mt-2">准备好开始了吗？</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Screen 5: 授权与付费 */}
        {currentScreen === 4 && (
          <motion.div
            key="screen-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md w-full"
          >
            <h2 className="mb-3 text-white">最后一步</h2>
            <p className="text-[#8E8E93] mb-8">为了给你最佳体验，我们需要访问以下数据</p>
            
            <div className="space-y-3 mb-8">
              <div className="bg-[#2C2C2E] rounded-xl p-4 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-[#FF375F]/20 flex items-center justify-center">
                  <Heart className="w-5 h-5 text-[#FF375F]" strokeWidth={2} />
                </div>
                <div className="flex-1 text-left">
                  <h4 className="text-white">健康数据</h4>
                  <p className="text-[#8E8E93]">睡眠、运动、心率等</p>
                </div>
              </div>
              
              <div className="bg-[#2C2C2E] rounded-xl p-4 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-[#FF9500]/20 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-[#FF9500]" strokeWidth={2} />
                </div>
                <div className="flex-1 text-left">
                  <h4 className="text-white">日历访问</h4>
                  <p className="text-[#8E8E93]">优化日程安排</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#0A84FF]/10 to-[#5E9FE6]/10 border border-[#0A84FF]/30 rounded-2xl p-6 mb-8">
              <p className="text-white mb-2">7天免费试用</p>
              <p className="text-[#0A84FF] mb-3">随后 ¥300/月</p>
              <p className="text-[#8E8E93]">随时可取消，无需承诺</p>
            </div>
            
            <Button 
              onClick={nextScreen}
              className="w-full bg-[#0A84FF] hover:bg-[#0A84FF]/90 text-white py-6 rounded-full mb-3"
            >
              开始免费试用
            </Button>
            
            <p className="text-[#8E8E93]">继续即表示您同意服务条款和隐私政策</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
