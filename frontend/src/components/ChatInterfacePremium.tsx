import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Send, Sparkles, TrendingUp, Battery, Moon, Sun } from "lucide-react";
import { CoachAvatarPremium } from "./CoachAvatarPremium";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

interface Message {
  id: string;
  type: "user" | "coach";
  content: string;
  timestamp: Date;
  insight?: {
    type: "energy" | "sleep" | "achievement";
    title: string;
    data?: { label: string; value: number; status: "good" | "normal" | "low" }[];
  };
}

interface ChatInterfacePremiumProps {
  coachType: "wise" | "companion" | "expert";
  onStartFocus?: () => void;
}

export function ChatInterfacePremium({ coachType, onStartFocus }: ChatInterfacePremiumProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "coach",
      content: "早上好！根据你的睡眠数据，昨晚的深度睡眠达到了2.5小时，恢复效果很不错。",
      timestamp: new Date(Date.now() - 3600000),
    },
    {
      id: "2",
      type: "coach",
      content: "我为你分析了本周的精力趋势，有一些有趣的发现：",
      timestamp: new Date(Date.now() - 3500000),
      insight: {
        type: "energy",
        title: "本周精力分析",
        data: [
          { label: "周一", value: 72, status: "normal" },
          { label: "周二", value: 85, status: "good" },
          { label: "周三", value: 68, status: "normal" },
          { label: "周四", value: 91, status: "good" },
          { label: "周五", value: 58, status: "low" },
          { label: "周六", value: 88, status: "good" },
          { label: "周日", value: 82, status: "good" }
        ]
      }
    },
    {
      id: "3",
      type: "user",
      content: "今天下午有个重要的客户演讲，感觉有点紧张",
      timestamp: new Date(Date.now() - 3000000),
    },
    {
      id: "4",
      type: "coach",
      content: "理解你的感受。根据你的精力曲线，下午2-3点是你状态最佳的时段。建议提前30分钟进入专注模式，通过深呼吸练习来调整状态。",
      timestamp: new Date(Date.now() - 2900000),
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const coachNames = {
    wise: "深思",
    companion: "温言",
    expert: "明策"
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date()
    };
    
    setMessages([...messages, newMessage]);
    setInputValue("");
    setIsTyping(true);

    // 模拟AI思考和回复
    setTimeout(() => {
      setIsTyping(false);
      const coachReply: Message = {
        id: (Date.now() + 1).toString(),
        type: "coach",
        content: "让我基于你的数据为你制定最优方案。根据分析，建议你...",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, coachReply]);
    }, 2000);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: "good" | "normal" | "low") => {
    switch (status) {
      case "good": return "#34C759";
      case "normal": return "#0A84FF";
      case "low": return "#FF9500";
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0C] flex flex-col relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%)",
            top: "10%",
            right: "-10%",
            filter: "blur(80px)"
          }}
          animate={{
            x: [0, -30, 0],
            y: [0, 30, 0]
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative bg-[#1C1C1E]/60 backdrop-blur-2xl border-b border-white/5 p-5"
      >
        <div className="flex items-center gap-4">
          <CoachAvatarPremium type={coachType} size="md" isActive />
          <div className="flex-1">
            <h3 className="text-white mb-1">{coachNames[coachType]}</h3>
            <div className="flex items-center gap-2">
              <motion.div
                className="w-2 h-2 rounded-full bg-[#34C759]"
                animate={{
                  opacity: [1, 0.5, 1],
                  scale: [1, 1.2, 1]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity
                }}
              />
              <p className="text-[#8E8E93]">智能在线</p>
            </div>
          </div>
          <Button
            onClick={onStartFocus}
            className="relative group bg-gradient-to-r from-[#667eea]/10 to-[#764ba2]/10 hover:from-[#667eea]/20 hover:to-[#764ba2]/20 text-[#667eea] border border-[#667eea]/20 hover:border-[#667eea]/40 px-6 py-3 rounded-full transition-all duration-300"
          >
            <Sparkles className="w-4 h-4 mr-2" strokeWidth={2} />
            <span>专注模式</span>
          </Button>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 relative">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ 
                delay: index * 0.05,
                duration: 0.4,
                ease: [0.16, 1, 0.3, 1]
              }}
              className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} gap-3 group`}
            >
              {message.type === "coach" && (
                <div className="flex-shrink-0">
                  <CoachAvatarPremium type={coachType} size="sm" />
                </div>
              )}
              
              <div className={`max-w-[75%] ${message.type === "user" ? "order-first" : ""}`}>
                {/* 消息气泡 */}
                <div className="relative">
                  {message.type === "coach" && (
                    <div className="absolute inset-0 bg-gradient-to-br from-[#667eea]/10 to-transparent rounded-3xl blur-xl" />
                  )}
                  
                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    className={`relative rounded-3xl p-5 backdrop-blur-xl transition-all ${
                      message.type === "user"
                        ? "bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white shadow-[0_8px_32px_rgba(102,126,234,0.25)]"
                        : "bg-[#1C1C1E]/80 border border-white/10 text-white group-hover:border-white/20"
                    }`}
                  >
                    <p className="leading-relaxed">{message.content}</p>
                    
                    {/* 智能洞察卡片 */}
                    {message.insight && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        transition={{ delay: 0.3 }}
                        className="mt-5 p-5 bg-black/20 backdrop-blur-sm rounded-2xl border border-white/10"
                      >
                        <div className="flex items-center gap-2 mb-4">
                          {message.insight.type === "energy" && <Battery className="w-4 h-4 text-[#0A84FF]" />}
                          {message.insight.type === "sleep" && <Moon className="w-4 h-4 text-[#BF5AF2]" />}
                          {message.insight.type === "achievement" && <TrendingUp className="w-4 h-4 text-[#34C759]" />}
                          <span className="text-sm text-white/80">{message.insight.title}</span>
                        </div>
                        
                        {message.insight.data && (
                          <div className="space-y-3">
                            {message.insight.data.map((item, idx) => (
                              <div key={idx}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs text-white/60">{item.label}</span>
                                  <span className="text-xs text-white/80">{item.value}%</span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${item.value}%` }}
                                    transition={{ 
                                      delay: 0.5 + idx * 0.08,
                                      duration: 0.8,
                                      ease: [0.16, 1, 0.3, 1]
                                    }}
                                    className="h-full rounded-full relative"
                                    style={{ 
                                      background: `linear-gradient(90deg, ${getStatusColor(item.status)}80, ${getStatusColor(item.status)})`
                                    }}
                                  >
                                    <motion.div
                                      className="absolute inset-0"
                                      animate={{
                                        opacity: [0.5, 1, 0.5]
                                      }}
                                      transition={{
                                        duration: 2,
                                        repeat: Infinity,
                                        ease: "easeInOut"
                                      }}
                                      style={{
                                        background: `linear-gradient(90deg, transparent, ${getStatusColor(item.status)}40, transparent)`
                                      }}
                                    />
                                  </motion.div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}
                  </motion.div>
                </div>
                
                <motion.p 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-[#8E8E93] mt-2 px-5 flex items-center gap-2"
                >
                  <span>{formatTime(message.timestamp)}</span>
                  {message.type === "coach" && (
                    <span className="text-xs bg-[#667eea]/20 text-[#667eea] px-2 py-0.5 rounded-full">
                      AI分析
                    </span>
                  )}
                </motion.p>
              </div>

              {message.type === "user" && (
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center shadow-lg">
                  <span className="text-white">我</span>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* 打字中指示器 */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-start gap-3"
            >
              <CoachAvatarPremium type={coachType} size="sm" />
              <div className="bg-[#1C1C1E]/80 backdrop-blur-xl border border-white/10 rounded-3xl px-6 py-4">
                <div className="flex gap-2">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 rounded-full bg-[#667eea]"
                      animate={{
                        y: [0, -8, 0],
                        opacity: [0.5, 1, 0.5]
                      }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        delay: i * 0.2
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative bg-[#1C1C1E]/60 backdrop-blur-2xl border-t border-white/5 p-5"
      >
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[#667eea]/20 to-[#764ba2]/20 rounded-full blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity" />
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="分享你的想法..."
              className="relative bg-[#2C2C2E]/80 backdrop-blur-xl border-white/10 focus:border-[#667eea]/50 text-white placeholder:text-[#8E8E93] rounded-full px-6 py-6 transition-all"
            />
          </div>
          
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="relative group bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:shadow-[0_0_30px_rgba(102,126,234,0.4)] text-white rounded-full w-14 h-14 p-0 disabled:opacity-30 disabled:hover:shadow-none transition-all duration-300"
          >
            <motion.div
              animate={inputValue.trim() ? { scale: [1, 1.1, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              <Send className="w-5 h-5" strokeWidth={2} />
            </motion.div>
          </Button>
        </div>

        {/* 智能建议提示 */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 flex items-center gap-2 text-xs text-[#8E8E93]"
        >
          <Sparkles className="w-3 h-3" />
          <span>AI教练会基于你的数据提供个性化建议</span>
        </motion.div>
      </motion.div>
    </div>
  );
}
