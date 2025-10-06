import { useState } from "react";
import { motion } from "motion/react";
import { Send, Activity, Moon } from "lucide-react";
import { CoachAvatar } from "./CoachAvatar";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

interface Message {
  id: string;
  type: "user" | "coach";
  content: string;
  timestamp: Date;
  data?: {
    type: "sleep" | "energy";
    values: number[];
    labels: string[];
  };
}

interface ChatInterfaceProps {
  coachType: "wise" | "companion" | "expert";
  onStartFocus?: () => void;
}

export function ChatInterface({ coachType, onStartFocus }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "coach",
      content: "早上好！我注意到你昨晚的睡眠质量不错，今天的精力应该会比较充沛。",
      timestamp: new Date(Date.now() - 3600000),
    },
    {
      id: "2",
      type: "coach",
      content: "根据你过去一周的数据，这是你的睡眠趋势：",
      timestamp: new Date(Date.now() - 3500000),
      data: {
        type: "sleep",
        values: [6.5, 7.2, 6.8, 7.5, 8.1, 7.3, 7.8],
        labels: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
      }
    },
    {
      id: "3",
      type: "user",
      content: "今天有个重要会议，有什么建议吗？",
      timestamp: new Date(Date.now() - 3000000),
    },
    {
      id: "4",
      type: "coach",
      content: "建议在会议前30分钟进入专注模式，做些简单的深呼吸练习。根据你的精力曲线，上午10-11点是你注意力最集中的时段。",
      timestamp: new Date(Date.now() - 2900000),
    }
  ]);
  const [inputValue, setInputValue] = useState("");

  const coachNames = {
    wise: "智者",
    companion: "伙伴",
    expert: "专家"
  };

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

    // 模拟AI回复
    setTimeout(() => {
      const coachReply: Message = {
        id: (Date.now() + 1).toString(),
        type: "coach",
        content: "我理解你的想法。让我根据你的数据分析一下最佳方案...",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, coachReply]);
    }, 1000);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-[#1C1C1E] flex flex-col">
      {/* Header */}
      <div className="bg-[#1C1C1E] border-b border-white/10 p-4 flex items-center gap-3">
        <CoachAvatar type={coachType} size="md" />
        <div className="flex-1">
          <h3 className="text-white">{coachNames[coachType]}</h3>
          <p className="text-[#8E8E93]">在线</p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onStartFocus}
          className="text-[#0A84FF] hover:text-[#0A84FF]/80 hover:bg-[#0A84FF]/10"
        >
          <Activity className="w-5 h-5 mr-2" strokeWidth={2} />
          专注模式
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} gap-3`}
          >
            {message.type === "coach" && (
              <CoachAvatar type={coachType} size="sm" />
            )}
            
            <div className={`max-w-[70%] ${message.type === "user" ? "order-first" : ""}`}>
              <div
                className={`rounded-2xl p-4 ${
                  message.type === "user"
                    ? "bg-[#0A84FF] text-white"
                    : "bg-[#2C2C2E] text-white"
                }`}
              >
                <p>{message.content}</p>
                
                {/* 数据卡片 */}
                {message.data && (
                  <div className="mt-4 bg-black/20 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      {message.data.type === "sleep" && (
                        <>
                          <Moon className="w-4 h-4" strokeWidth={2} />
                          <span className="text-sm opacity-80">睡眠时长 (小时)</span>
                        </>
                      )}
                    </div>
                    
                    {/* 简单的条形图 */}
                    <div className="space-y-2">
                      {message.data.values.map((value, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <span className="text-xs opacity-60 w-8">{message.data!.labels[idx]}</span>
                          <div className="flex-1 bg-white/10 rounded-full h-2 overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${(value / 10) * 100}%` }}
                              transition={{ delay: 0.5 + idx * 0.1, duration: 0.5 }}
                              className="h-full bg-[#34C759] rounded-full"
                            />
                          </div>
                          <span className="text-xs opacity-80 w-8">{value}h</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <p className="text-[#8E8E93] mt-1 px-4">
                {formatTime(message.timestamp)}
              </p>
            </div>

            {message.type === "user" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#0A84FF] to-[#5E9FE6] flex items-center justify-center">
                <span className="text-white">我</span>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Input */}
      <div className="bg-[#1C1C1E] border-t border-white/10 p-4">
        <div className="flex gap-3">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="输入消息..."
            className="flex-1 bg-[#2C2C2E] border-none text-white placeholder:text-[#8E8E93] rounded-full px-6"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="bg-[#0A84FF] hover:bg-[#0A84FF]/90 text-white rounded-full w-12 h-12 p-0 disabled:opacity-30"
          >
            <Send className="w-5 h-5" strokeWidth={2} />
          </Button>
        </div>
      </div>
    </div>
  );
}
