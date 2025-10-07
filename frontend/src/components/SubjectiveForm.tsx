/**
 * 主观评估专项表单
 * 支持能量水平、心情、专注度的可视化录入
 */

import { useState } from "react";
import { motion } from "motion/react";
import { Zap, Smile, Target, Save, History } from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { useHealthStore } from "../store/healthStore";
import { HealthDataType, HealthDataSource } from "../api";

interface SubjectiveFormProps {
  onComplete: () => void;
  onCancel: () => void;
  onViewHistory: (dataType: string) => void;
}

// 表情符号映射
const ENERGY_EMOJIS = ["😴", "😪", "😐", "🙂", "😊", "😃", "😎", "⚡", "🔥", "💪"];
const MOOD_EMOJIS = ["😢", "😞", "😕", "😐", "🙂", "😊", "😄", "😁", "🥳", "😍"];
const FOCUS_EMOJIS = ["😵", "😶", "😑", "🤔", "😯", "🧐", "🎯", "💡", "🔥", "⚡"];

// 心情标签快捷选择
const MOOD_TAGS = [
  { emoji: "😢", label: "低落", value: 2 },
  { emoji: "😰", label: "焦虑", value: 3 },
  { emoji: "😐", label: "平静", value: 5 },
  { emoji: "😊", label: "愉快", value: 7 },
  { emoji: "😍", label: "兴奋", value: 9 },
  { emoji: "😴", label: "疲惫", value: 4 },
  { emoji: "😤", label: "烦躁", value: 3 },
  { emoji: "🥳", label: "开心", value: 10 },
];

export function SubjectiveForm({
  onComplete,
  onCancel,
  onViewHistory,
}: SubjectiveFormProps) {
  const { createBatch, isLoading } = useHealthStore();

  // 三项评估分数 (1-10)
  const [energyLevel, setEnergyLevel] = useState([7]);
  const [mood, setMood] = useState([7]);
  const [focus, setFocus] = useState([7]);

  // 记录时间
  const [recordedDate, setRecordedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [recordedTime, setRecordedTime] = useState(
    new Date().toTimeString().slice(0, 5)
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const recordedAt = new Date(`${recordedDate}T${recordedTime}`).toISOString();

    // 批量创建3条数据
    const batchData = [
      {
        data_type: HealthDataType.ENERGY_LEVEL,
        value: energyLevel[0],
        unit: "分",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      },
      {
        data_type: HealthDataType.MOOD,
        value: mood[0],
        unit: "分",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      },
      {
        data_type: HealthDataType.FOCUS,
        value: focus[0],
        unit: "分",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      },
    ];

    const result = await createBatch(batchData);

    if (result) {
      alert("主观评估数据录入成功!");
      onComplete();
    }
  };

  // 获取描述文字
  const getEnergyText = (value: number) => {
    if (value <= 3) return "精疲力竭";
    if (value <= 5) return "有些疲惫";
    if (value <= 7) return "精力充沛";
    return "状态极佳";
  };

  const getMoodText = (value: number) => {
    if (value <= 3) return "情绪低落";
    if (value <= 5) return "心情平静";
    if (value <= 7) return "愉快开心";
    return "非常兴奋";
  };

  const getFocusText = (value: number) => {
    if (value <= 3) return "难以集中";
    if (value <= 5) return "一般专注";
    if (value <= 7) return "较好专注";
    return "高度专注";
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-5 sm:space-y-6"
    >
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">主观评估</h2>
        <p className="text-white/60 text-sm sm:text-base">记录您的能量、心情和专注状态</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 lg:space-y-6">
        {/* 能量水平 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
          <div className="flex items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#FFD700]/20 flex items-center justify-center">
              <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-[#FFD700]" strokeWidth={2} />
            </div>
            <Label className="text-white font-medium text-sm sm:text-base">能量水平</Label>
          </div>

          <div className="text-center mb-3 sm:mb-4">
            <div className="text-5xl sm:text-6xl mb-1 sm:mb-2">
              {ENERGY_EMOJIS[energyLevel[0] - 1]}
            </div>
            <div className="text-white text-lg sm:text-xl font-bold">
              {energyLevel[0]} 分
            </div>
            <div className="text-white/60 text-xs sm:text-sm">
              {getEnergyText(energyLevel[0])}
            </div>
          </div>

          <Slider
            value={energyLevel}
            onValueChange={setEnergyLevel}
            min={1}
            max={10}
            step={1}
            className="py-4"
          />

          <div className="flex justify-between text-white/40 text-xs">
            <span>😴 低</span>
            <span>💪 高</span>
          </div>
        </div>

        {/* 心情状态 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
          <div className="flex items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#FF69B4]/20 flex items-center justify-center">
              <Smile className="w-4 h-4 sm:w-5 sm:h-5 text-[#FF69B4]" strokeWidth={2} />
            </div>
            <Label className="text-white font-medium text-sm sm:text-base">心情状态</Label>
          </div>

          <div className="text-center mb-3 sm:mb-4">
            <div className="text-5xl sm:text-6xl mb-1 sm:mb-2">{MOOD_EMOJIS[mood[0] - 1]}</div>
            <div className="text-white text-lg sm:text-xl font-bold">{mood[0]} 分</div>
            <div className="text-white/60 text-xs sm:text-sm">{getMoodText(mood[0])}</div>
          </div>

          <Slider
            value={mood}
            onValueChange={setMood}
            min={1}
            max={10}
            step={1}
            className="py-4"
          />

          <div className="flex justify-between text-white/40 text-xs">
            <span>😢 低落</span>
            <span>🥳 开心</span>
          </div>

          {/* 快捷心情标签 */}
          <div>
            <Label className="text-white/60 text-xs mb-2 block">
              快捷选择:
            </Label>
            <div className="grid grid-cols-4 gap-2">
              {MOOD_TAGS.map((tag) => (
                <button
                  key={tag.label}
                  type="button"
                  onClick={() => setMood([tag.value])}
                  className={`bg-white/5 hover:bg-white/15 rounded-xl p-2 sm:p-2.5 transition-all text-center touch-target ${
                    mood[0] === tag.value ? "ring-2 ring-white/50" : ""
                  }`}
                >
                  <div className="text-xl sm:text-2xl mb-0.5 sm:mb-1">{tag.emoji}</div>
                  <div className="text-white text-[10px] sm:text-xs">{tag.label}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 专注程度 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
          <div className="flex items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#00BCD4]/20 flex items-center justify-center">
              <Target className="w-4 h-4 sm:w-5 sm:h-5 text-[#00BCD4]" strokeWidth={2} />
            </div>
            <Label className="text-white font-medium text-sm sm:text-base">专注程度</Label>
          </div>

          <div className="text-center mb-3 sm:mb-4">
            <div className="text-5xl sm:text-6xl mb-1 sm:mb-2">{FOCUS_EMOJIS[focus[0] - 1]}</div>
            <div className="text-white text-lg sm:text-xl font-bold">{focus[0]} 分</div>
            <div className="text-white/60 text-xs sm:text-sm">
              {getFocusText(focus[0])}
            </div>
          </div>

          <Slider
            value={focus}
            onValueChange={setFocus}
            min={1}
            max={10}
            step={1}
            className="py-4"
          />

          <div className="flex justify-between text-white/40 text-xs">
            <span>😵 分散</span>
            <span>🔥 集中</span>
          </div>
        </div>

        {/* 记录时间 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
          <Label className="text-white text-xs sm:text-sm">记录时间</Label>
          <div className="grid grid-cols-2 gap-2 sm:gap-3">
            <input
              type="date"
              value={recordedDate}
              onChange={(e) => setRecordedDate(e.target.value)}
              className="bg-white/5 border border-white/20 text-white rounded-xl px-3 py-2.5 sm:px-4 sm:py-3 text-sm sm:text-base"
            />
            <input
              type="time"
              value={recordedTime}
              onChange={(e) => setRecordedTime(e.target.value)}
              className="bg-white/5 border border-white/20 text-white rounded-xl px-3 py-2.5 sm:px-4 sm:py-3 text-sm sm:text-base"
            />
          </div>
        </div>

        {/* 按钮组 */}
        <div className="flex gap-2 sm:gap-3 pt-3 sm:pt-4">
          <Button
            type="button"
            onClick={() => onViewHistory(HealthDataType.ENERGY_LEVEL)}
            variant="outline"
            className="flex-1 bg-white/10 border-white/20 text-white hover:bg-white/20 touch-target px-4 py-3 sm:px-5 sm:py-4 text-sm sm:text-base"
          >
            <History className="w-4 h-4 mr-1.5 sm:mr-2" />
            <span className="hidden sm:inline">查看历史</span>
            <span className="sm:hidden">历史</span>
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-white text-[#2B69B6] hover:bg-white/90 touch-target px-4 py-3 sm:px-5 sm:py-4 text-sm sm:text-base"
          >
            <Save className="w-4 h-4 mr-1.5 sm:mr-2" />
            {isLoading ? "保存中..." : "批量保存"}
          </Button>
        </div>

        <Button
          type="button"
          onClick={onCancel}
          variant="ghost"
          className="w-full text-white/60 hover:text-white hover:bg-white/5 touch-target py-3 sm:py-4 text-sm sm:text-base"
        >
          取消
        </Button>
      </form>

      {/* 提示信息 */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4">
        <p className="text-white/60 text-sm text-center">
          💡 一次保存能量、心情、专注3项数据
        </p>
      </div>
    </motion.div>
  );
}
