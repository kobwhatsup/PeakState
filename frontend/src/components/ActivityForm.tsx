/**
 * 活动数据专项表单
 * 支持步数、距离、能量、运动时长的智能录入
 */

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Activity, Zap, Save, History } from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { useHealthStore } from "../store/healthStore";
import { HealthDataType, HealthDataSource } from "../api";

interface ActivityFormProps {
  onComplete: () => void;
  onCancel: () => void;
  onViewHistory: (dataType: string) => void;
}

// 运动类型模板
const ACTIVITY_TEMPLATES = [
  {
    emoji: "🏃",
    label: "跑步",
    steps: 6000,
    distance: 5.0,
    energy: 400,
    duration: 30,
  },
  {
    emoji: "🚶",
    label: "散步",
    steps: 5000,
    distance: 3.5,
    energy: 150,
    duration: 60,
  },
  {
    emoji: "🚴",
    label: "骑行",
    steps: 0,
    distance: 10.0,
    energy: 300,
    duration: 45,
  },
  {
    emoji: "🏊",
    label: "游泳",
    steps: 0,
    distance: 1.0,
    energy: 500,
    duration: 60,
  },
  {
    emoji: "🧘",
    label: "瑜伽",
    steps: 0,
    distance: 0,
    energy: 100,
    duration: 45,
  },
  {
    emoji: "💪",
    label: "力量",
    steps: 0,
    distance: 0,
    energy: 250,
    duration: 40,
  },
];

// 快捷步数
const QUICK_STEPS = [5000, 8000, 10000, 12000];

export function ActivityForm({
  onComplete,
  onCancel,
  onViewHistory,
}: ActivityFormProps) {
  const { createBatch, isLoading } = useHealthStore();

  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [steps, setSteps] = useState("");
  const [distance, setDistance] = useState("");
  const [energy, setEnergy] = useState("");
  const [duration, setDuration] = useState("");

  const [recordedDate, setRecordedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [recordedTime, setRecordedTime] = useState(
    new Date().toTimeString().slice(0, 5)
  );

  // 智能联动计算
  useEffect(() => {
    const stepsNum = parseFloat(steps);
    if (!isNaN(stepsNum) && stepsNum > 0) {
      // 根据步数估算距离 (平均步长0.7米)
      const estimatedDistance = (stepsNum * 0.7) / 1000;
      if (!distance || parseFloat(distance) === 0) {
        setDistance(estimatedDistance.toFixed(1));
      }

      // 根据步数估算能量消耗 (平均每1000步消耗50千卡)
      const estimatedEnergy = (stepsNum / 1000) * 50;
      if (!energy || parseFloat(energy) === 0) {
        setEnergy(Math.round(estimatedEnergy).toString());
      }
    }
  }, [steps]);

  const handleTemplateSelect = (template: typeof ACTIVITY_TEMPLATES[0]) => {
    setSelectedTemplate(template.label);
    setSteps(template.steps.toString());
    setDistance(template.distance.toString());
    setEnergy(template.energy.toString());
    setDuration(template.duration.toString());
  };

  const handleQuickSteps = (quickSteps: number) => {
    setSteps(quickSteps.toString());
    setSelectedTemplate(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const recordedAt = new Date(`${recordedDate}T${recordedTime}`).toISOString();

    // 构建批量数据 (仅包含填写的字段)
    const batchData: any[] = [];

    if (steps && parseFloat(steps) > 0) {
      batchData.push({
        data_type: HealthDataType.STEPS,
        value: parseFloat(steps),
        unit: "步",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      });
    }

    if (distance && parseFloat(distance) > 0) {
      batchData.push({
        data_type: HealthDataType.DISTANCE,
        value: parseFloat(distance),
        unit: "公里",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      });
    }

    if (energy && parseFloat(energy) > 0) {
      batchData.push({
        data_type: HealthDataType.ACTIVE_ENERGY,
        value: parseFloat(energy),
        unit: "千卡",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      });
    }

    if (duration && parseFloat(duration) > 0) {
      batchData.push({
        data_type: HealthDataType.EXERCISE_MINUTES,
        value: parseFloat(duration),
        unit: "分钟",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      });
    }

    if (batchData.length === 0) {
      alert("请至少填写一项活动数据");
      return;
    }

    const result = await createBatch(batchData);

    if (result) {
      alert(`活动数据录入成功! 共保存${batchData.length}条记录`);
      onComplete();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* 标题 */}
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-[#4CAF50]/20 flex items-center justify-center">
          <Activity className="w-8 h-8 text-[#4CAF50]" strokeWidth={2} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">活动数据</h2>
          <p className="text-white/60">记录运动和活动信息</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 运动类型模板 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">运动类型 (可选)</Label>
          <div className="grid grid-cols-3 gap-2">
            {ACTIVITY_TEMPLATES.map((template) => (
              <button
                key={template.label}
                type="button"
                onClick={() => handleTemplateSelect(template)}
                className={`bg-white/5 hover:bg-white/15 rounded-xl p-3 transition-all text-center ${
                  selectedTemplate === template.label
                    ? "ring-2 ring-[#4CAF50]"
                    : ""
                }`}
              >
                <div className="text-3xl mb-1">{template.emoji}</div>
                <div className="text-white text-xs">{template.label}</div>
              </button>
            ))}
          </div>
          {selectedTemplate && (
            <p className="text-white/60 text-xs text-center">
              已应用 {selectedTemplate} 模板,可手动调整
            </p>
          )}
        </div>

        {/* 步数 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">步数</Label>

          <div className="flex items-center gap-3">
            <Input
              type="number"
              value={steps}
              onChange={(e) => {
                setSteps(e.target.value);
                setSelectedTemplate(null);
              }}
              placeholder="输入步数"
              className="flex-1 bg-white/5 border-white/20 text-white text-xl h-14 text-center"
            />
            <span className="text-white/60 min-w-[40px]">步</span>
          </div>

          <div className="flex gap-2">
            {QUICK_STEPS.map((quickStep) => (
              <button
                key={quickStep}
                type="button"
                onClick={() => handleQuickSteps(quickStep)}
                className="flex-1 bg-white/5 hover:bg-white/15 rounded-lg py-2 text-white text-sm transition-all"
              >
                {(quickStep / 1000).toFixed(0)}K
              </button>
            ))}
          </div>

          {steps && parseFloat(steps) > 0 && (
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-white/60 text-sm mb-1">今日进度</div>
              <div className="flex items-center justify-center gap-2">
                <div className="text-white text-lg font-bold">
                  {parseFloat(steps).toLocaleString()}
                </div>
                <div className="text-white/40 text-sm">/ 10,000</div>
              </div>
              <div className="w-full bg-white/10 h-2 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-[#4CAF50] h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min((parseFloat(steps) / 10000) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* 其他指标 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">其他指标 (可选)</Label>

          {/* 距离 */}
          <div>
            <Label className="text-white/60 text-sm mb-2 block">距离</Label>
            <div className="flex items-center gap-3">
              <Input
                type="number"
                step="0.1"
                value={distance}
                onChange={(e) => setDistance(e.target.value)}
                placeholder="自动估算"
                className="flex-1 bg-white/5 border-white/20 text-white"
              />
              <span className="text-white/60 min-w-[50px]">公里</span>
            </div>
          </div>

          {/* 活动能量 */}
          <div>
            <Label className="text-white/60 text-sm mb-2 block">
              活动能量
            </Label>
            <div className="flex items-center gap-3">
              <Input
                type="number"
                value={energy}
                onChange={(e) => setEnergy(e.target.value)}
                placeholder="自动估算"
                className="flex-1 bg-white/5 border-white/20 text-white"
              />
              <span className="text-white/60 min-w-[50px]">千卡</span>
            </div>
          </div>

          {/* 运动时长 */}
          <div>
            <Label className="text-white/60 text-sm mb-2 block">
              运动时长
            </Label>
            <div className="flex items-center gap-3">
              <Input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="输入时长"
                className="flex-1 bg-white/5 border-white/20 text-white"
              />
              <span className="text-white/60 min-w-[50px]">分钟</span>
            </div>
          </div>

          <p className="text-white/40 text-xs">
            💡 基于步数自动计算距离和能量,可手动调整
          </p>
        </div>

        {/* 记录时间 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white text-sm">记录时间</Label>
          <div className="grid grid-cols-2 gap-3">
            <Input
              type="date"
              value={recordedDate}
              onChange={(e) => setRecordedDate(e.target.value)}
              className="bg-white/5 border-white/20 text-white"
            />
            <Input
              type="time"
              value={recordedTime}
              onChange={(e) => setRecordedTime(e.target.value)}
              className="bg-white/5 border-white/20 text-white"
            />
          </div>
        </div>

        {/* 按钮组 */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            onClick={() => onViewHistory(HealthDataType.STEPS)}
            variant="outline"
            className="flex-1 bg-white/10 border-white/20 text-white hover:bg-white/20"
          >
            <History className="w-4 h-4 mr-2" />
            查看历史
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-white text-[#2B69B6] hover:bg-white/90"
          >
            <Save className="w-4 h-4 mr-2" />
            {isLoading ? "保存中..." : "保存活动数据"}
          </Button>
        </div>

        <Button
          type="button"
          onClick={onCancel}
          variant="ghost"
          className="w-full text-white/60 hover:text-white hover:bg-white/5"
        >
          取消
        </Button>
      </form>
    </motion.div>
  );
}
