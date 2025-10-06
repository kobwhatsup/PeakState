import { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import { Send, Zap, Battery, TrendingUp, ArrowLeft } from "lucide-react";
import { CoachAvatarElite } from "./CoachAvatarElite";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useChatStore } from "../store/chatStore";
import { useAuthStore } from "../store/authStore";
import type { CoachType } from "../api";

interface ChatInterfaceEliteProps {
  coachType: CoachType;
  onStartFocus?: () => void;
}

export function ChatInterfaceElite({ coachType, onStartFocus }: ChatInterfaceEliteProps) {
  const {
    messages,
    currentConversationId,
    isSending,
    sendMessage,
    createConversation,
    loadConversations,
  } = useChatStore();

  const { user } = useAuthStore();
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初始化：加载对话列表
  useEffect(() => {
    const initChat = async () => {
      try {
        console.log("ChatInterface init - loading conversations");
        await loadConversations();
        console.log("Conversations loaded");
      } catch (error) {
        console.error("Failed to load conversations:", error);
      }
    };
    initChat();
  }, [loadConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isSending) return;

    const content = inputValue;
    setInputValue("");

    try {
      // 如果没有当前对话，先创建一个
      if (!currentConversationId) {
        console.log("No current conversation, creating one...");
        const conversationId = await createConversation(coachType, "新对话");
        console.log("Conversation created with ID:", conversationId);
      }

      console.log("Sending message to conversation:", currentConversationId);
      await sendMessage(content);
      console.log("Message sent successfully");
    } catch (error) {
      console.error("Failed to send message:", error);
      // 如果发送失败，恢复输入内容
      setInputValue(content);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  const coachNames: Record<CoachType, string> = {
    mentor: "智慧导师",
    coach: "能量教练",
    doctor: "健康医生",
    zen: "禅意大师"
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* 统一的背景装饰 - 与首页一致 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-[800px] h-[800px] rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 60%)",
            top: "-20%",
            left: "50%",
            transform: "translateX(-50%)",
            filter: "blur(100px)"
          }}
        />
        <div
          className="absolute w-[600px] h-[600px] rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(77, 208, 225, 0.08) 0%, transparent 70%)",
            bottom: "10%",
            right: "-10%",
            filter: "blur(80px)"
          }}
        />
      </div>

      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative bg-white/10 backdrop-blur-xl border-b border-white/20 p-6"
      >
        <div className="flex items-center gap-5">
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-white/10 rounded-full"
          >
            <ArrowLeft className="w-5 h-5" strokeWidth={1.5} />
          </Button>
          
          <CoachAvatarElite type={coachType} size="md" isActive />
          
          <div className="flex-1">
            <h3 className="text-white mb-1">{coachNames[coachType]}</h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#4DD0E1]" />
              <p className="text-white/80 text-sm">在线</p>
            </div>
          </div>
          
          <Button
            onClick={onStartFocus}
            className="bg-white/20 hover:bg-white/30 text-white border border-white/30 hover:border-white/40 px-6 py-3 rounded-2xl transition-all duration-300 backdrop-blur-sm"
          >
            <Zap className="w-4 h-4 mr-2" strokeWidth={1.5} />
            <span>专注模式</span>
          </Button>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 relative">
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex gap-4 ${message.role === "user" ? "flex-row-reverse" : "flex-row"} items-start`}
          >
            {message.role === "assistant" && <CoachAvatarElite type={coachType} size="sm" />}

            <div className={`max-w-[70%] ${message.role === "user" ? "items-end" : "items-start"} flex flex-col`}>
              {/* 消息卡片 */}
              <div
                className={`rounded-3xl p-6 backdrop-blur-xl ${
                  message.role === "user"
                    ? "bg-white/20 text-white shadow-lg shadow-black/10 border border-white/30"
                    : "bg-white/95 border border-white/50 text-[#2B69B6] shadow-lg shadow-black/5"
                }`}
              >
                <p className="leading-relaxed">{message.content}</p>

                {/* 能量级别卡片 - 暂时移除，后续从metadata解析 */}
                {message.metadata?.insight && message.metadata.insight.type === "energy" && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    transition={{ delay: 0.3 }}
                    className="mt-6 space-y-6"
                  >
                    {/* 圆环图表区域 */}
                    <div className="flex items-center justify-center py-8">
                      <svg className="w-48 h-48 transform -rotate-90">
                        <circle
                          cx="96"
                          cy="96"
                          r="80"
                          fill="none"
                          stroke="#E8F4F8"
                          strokeWidth="16"
                        />
                        {message.metadata?.insight.data?.map((item, idx) => {
                          const total = message.metadata?.insight?.data?.reduce((sum, d) => sum + d.value, 0) || 100;
                          const percentage = (item.value / total) * 100;
                          const circumference = 2 * Math.PI * 80;
                          const previousPercentages = message.metadata?.insight?.data?.slice(0, idx).reduce((sum, d) => sum + (d.value / total) * 100, 0) || 0;
                          const offset = circumference - (circumference * previousPercentages / 100);
                          const dashArray = (circumference * percentage / 100);
                          
                          return (
                            <motion.circle
                              key={idx}
                              cx="96"
                              cy="96"
                              r="80"
                              fill="none"
                              stroke={item.color}
                              strokeWidth="16"
                              strokeDasharray={`${dashArray} ${circumference}`}
                              strokeDashoffset={-offset}
                              strokeLinecap="round"
                              initial={{ strokeDashoffset: -circumference }}
                              animate={{ strokeDashoffset: -offset }}
                              transition={{ duration: 1, delay: idx * 0.1 }}
                            />
                          );
                        })}
                      </svg>
                    </div>

                    {/* 能量指标列表 */}
                    <div className="space-y-5">
                      {message.metadata?.insight.data?.map((item, idx) => (
                        <div key={idx} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-[#2B69B6]">{item.label}</span>
                            <span className="text-sm text-[#2B69B6]">{item.value}%</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-1.5 bg-[#E8F4F8] rounded-full overflow-hidden">
                              <motion.div
                                className="h-full rounded-full"
                                style={{ backgroundColor: item.color }}
                                initial={{ width: 0 }}
                                animate={{ width: `${item.value}%` }}
                                transition={{ duration: 0.8, delay: 0.5 + idx * 0.1 }}
                              />
                            </div>
                            <div 
                              className="w-8 h-8 rounded-full flex items-center justify-center"
                              style={{ backgroundColor: `${item.color}20` }}
                            >
                              <div 
                                className="w-4 h-4 rounded-full"
                                style={{ backgroundColor: item.color }}
                              />
                            </div>
                          </div>
                          <p className="text-xs text-[#2B69B6]/60">Daily</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>

              <p className="text-white/60 text-sm mt-3 px-5">
                {formatTime(new Date(message.timestamp))}
              </p>
            </div>

            {message.role === "user" && (
              <div 
                className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white"
                style={{
                  background: "rgba(255, 255, 255, 0.25)",
                  backdropFilter: "blur(10px)"
                }}
              >
                我
              </div>
            )}
          </motion.div>
        ))}

        {/* 打字中指示器 */}
        {isSending && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-start gap-4"
          >
            <CoachAvatarElite type={coachType} size="sm" />
            <div className="bg-white/95 backdrop-blur-xl border border-white/50 rounded-3xl px-7 py-5">
              <div className="flex gap-2">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-[#4DD0E1]"
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

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative bg-white/10 backdrop-blur-xl border-t border-white/20 p-6"
      >
        <div className="flex gap-4 items-end max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="输入您的问题..."
              className="bg-white/15 backdrop-blur-xl border-white/30 focus:border-white/50 text-white placeholder:text-white/60 rounded-2xl px-6 py-6 transition-all"
            />
          </div>
          
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="bg-white/90 hover:bg-white text-[#2B69B6] rounded-2xl w-14 h-14 p-0 disabled:opacity-30 shadow-lg shadow-black/10 hover:shadow-xl hover:shadow-black/15 transition-all duration-300"
          >
            <Send className="w-5 h-5" strokeWidth={1.5} />
          </Button>
        </div>
      </motion.div>
    </div>
  );
}