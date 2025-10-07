/**
 * 心率/HRV数据专项表单
 * 支持实时健康评估和范围提示
 */

import { useState, useMemo } from "react";
import { motion } from "motion/react";
import { Heart, AlertTriangle, CheckCircle, Save, History } from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { useHealthStore } from "../store/healthStore";
import { HealthDataType, HealthDataSource } from "../api";

interface HeartRateFormProps {
  onComplete: () => void;
  onCancel: () => void;
  onViewHistory: (dataType: string) => void;
}

// 健康范围配置
const HEALTH_RANGES: Record<
  string,
  {
    min: number;
    max: number;
    healthy: [number, number];
    unit: string;
    label: string;
  }
> = {
  [HealthDataType.HEART_RATE_RESTING]: {
    min: 30,
    max: 150,
    healthy: [50, 90],
    unit: "bpm",
    label: "静息心率",
  },
  [HealthDataType.HEART_RATE]: {
    min: 40,
    max: 220,
    healthy: [60, 100],
    unit: "bpm",
    label: "心率",
  },
  [HealthDataType.HEART_RATE_WALKING]: {
    min: 60,
    max: 180,
    healthy: [90, 120],
    unit: "bpm",
    label: "步行心率",
  },
  [HealthDataType.HRV]: {
    min: 10,
    max: 300,
    healthy: [20, 200],
    unit: "ms",
    label: "心率变异性",
  },
  [HealthDataType.HRV_RMSSD]: {
    min: 10,
    max: 250,
    healthy: [20, 150],
    unit: "ms",
    label: "HRV RMSSD",
  },
  [HealthDataType.HRV_SDNN]: {
    min: 10,
    max: 300,
    healthy: [30, 200],
    unit: "ms",
    label: "HRV SDNN",
  },
};

// 心率数据类型选项
const HEART_RATE_TYPES = [
  { value: HealthDataType.HEART_RATE_RESTING, label: "静息心率" },
  { value: HealthDataType.HEART_RATE, label: "实时心率" },
  { value: HealthDataType.HEART_RATE_WALKING, label: "步行心率" },
  { value: HealthDataType.HRV, label: "HRV (心率变异性)" },
  { value: HealthDataType.HRV_RMSSD, label: "HRV RMSSD" },
  { value: HealthDataType.HRV_SDNN, label: "HRV SDNN" },
];

export function HeartRateForm({
  onComplete,
  onCancel,
  onViewHistory,
}: HeartRateFormProps) {
  const { createData, isLoading } = useHealthStore();

  const [dataType, setDataType] = useState(HealthDataType.HEART_RATE_RESTING);
  const [value, setValue] = useState("");

  const [recordedDate, setRecordedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [recordedTime, setRecordedTime] = useState(
    new Date().toTimeString().slice(0, 5)
  );

  const config = HEALTH_RANGES[dataType];

  // 健康评估
  const assessment = useMemo(() => {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return null;

    const { min, max, healthy } = config;

    if (numValue < min || numValue > max) {
      return {
        status: "error",
        message: `数值超出合理范围 (${min}-${max} ${config.unit})`,
        color: "#F44336",
        icon: AlertTriangle,
      };
    }

    if (numValue < healthy[0] || numValue > healthy[1]) {
      return {
        status: "warning",
        message: `数值偏离健康范围 (${healthy[0]}-${healthy[1]} ${config.unit})`,
        color: "#FF9800",
        icon: AlertTriangle,
      };
    }

    return {
      status: "healthy",
      message: "数据在健康范围内",
      color: "#4CAF50",
      icon: CheckCircle,
    };
  }, [value, config]);

  // 计算指示器位置
  const indicatorPosition = useMemo(() => {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return 50;

    const { min, max } = config;
    const position = ((numValue - min) / (max - min)) * 100;
    return Math.max(0, Math.min(100, position));
  }, [value, config]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!value || parseFloat(value) <= 0) {
      alert("请输入有效的数值");
      return;
    }

    if (assessment?.status === "error") {
      const confirm = window.confirm(
        "数值超出合理范围，确定要保存吗？建议重新确认数据准确性。"
      );
      if (!confirm) return;
    }

    const recordedAt = new Date(`${recordedDate}T${recordedTime}`).toISOString();

    const result = await createData({
      data_type: dataType,
      value: parseFloat(value),
      unit: config.unit,
      source: HealthDataSource.MANUAL,
      recorded_at: recordedAt,
    });

    if (result) {
      alert(`${config.label}录入成功!`);
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
        <div className="w-16 h-16 rounded-full bg-[#FF5252]/20 flex items-center justify-center">
          <Heart className="w-8 h-8 text-[#FF5252]" strokeWidth={2} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">心率数据</h2>
          <p className="text-white/60">记录心率和HRV信息</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 数据类型选择 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">数据类型</Label>
          <select
            value={dataType}
            onChange={(e) => {
              setDataType(e.target.value);
              setValue(""); // 清空数值
            }}
            className="w-full bg-white/5 border border-white/20 text-white rounded-xl px-4 py-3"
          >
            {HEART_RATE_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* 数值输入 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">{config.label}</Label>

          <div className="flex items-center gap-3">
            <Input
              type="number"
              step="0.1"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={`输入${config.label}`}
              className="flex-1 bg-white/5 border-white/20 text-white text-2xl h-16 text-center"
              required
            />
            <span className="text-white/60 text-lg min-w-[60px]">
              {config.unit}
            </span>
          </div>

          {/* 健康范围指示器 */}
          {value && (
            <div className="space-y-3">
              <div className="relative h-3 bg-white/10 rounded-full overflow-hidden">
                {/* 健康范围区域 */}
                <div
                  className="absolute h-full bg-gradient-to-r from-transparent via-[#4CAF50]/30 to-transparent"
                  style={{
                    left: `${((config.healthy[0] - config.min) / (config.max - config.min)) * 100}%`,
                    right: `${100 - ((config.healthy[1] - config.min) / (config.max - config.min)) * 100}%`,
                  }}
                />

                {/* 当前值指示器 */}
                <motion.div
                  className="absolute top-0 bottom-0 w-1"
                  style={{
                    left: `${indicatorPosition}%`,
                    backgroundColor: assessment?.color || "#fff",
                  }}
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ duration: 0.3 }}
                />
              </div>

              <div className="flex justify-between text-white/40 text-xs">
                <span>低 ({config.min})</span>
                <span>健康范围: {config.healthy[0]}-{config.healthy[1]}</span>
                <span>高 ({config.max})</span>
              </div>

              {/* 评估结果 */}
              {assessment && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex items-center gap-2 p-3 rounded-xl ${
                    assessment.status === "healthy"
                      ? "bg-[#4CAF50]/10"
                      : assessment.status === "warning"
                        ? "bg-[#FF9800]/10"
                        : "bg-[#F44336]/10"
                  }`}
                >
                  <assessment.icon
                    className="w-5 h-5"
                    style={{ color: assessment.color }}
                    strokeWidth={2}
                  />
                  <span
                    className="text-sm font-medium"
                    style={{ color: assessment.color }}
                  >
                    {assessment.message}
                  </span>
                </motion.div>
              )}
            </div>
          )}
        </div>

        {/* 健康建议 */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4">
          <p className="text-white/60 text-sm">
            💡 <strong>正常范围</strong>: {config.healthy[0]}-{config.healthy[1]}{" "}
            {config.unit}
          </p>
          {dataType === HealthDataType.HEART_RATE_RESTING && (
            <p className="text-white/40 text-xs mt-2">
              建议清晨醒来后、保持静止状态5分钟再测量
            </p>
          )}
          {dataType.includes("hrv") && (
            <p className="text-white/40 text-xs mt-2">
              HRV越高通常表示心脏健康状况越好,压力越低
            </p>
          )}
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
            onClick={() => onViewHistory(dataType)}
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
            {isLoading ? "保存中..." : "保存"}
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
