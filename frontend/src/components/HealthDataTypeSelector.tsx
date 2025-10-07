/**
 * 健康数据类型选择器
 * 提供分类图标展示和快速搜索
 */

import { motion } from "motion/react";
import {
  Moon,
  Heart,
  Activity,
  Brain,
  Thermometer,
  Wind,
  Droplets,
  Zap,
  Smile,
  Target,
} from "lucide-react";
import { HealthDataType } from "../api";

export interface DataTypeConfig {
  type: string;
  icon: React.ComponentType<any>;
  label: string;
  unit: string;
  category: "sleep" | "heart" | "activity" | "subjective" | "other";
  color: string;
}

export const DATA_TYPE_CONFIGS: Record<string, DataTypeConfig> = {
  // 睡眠
  [HealthDataType.SLEEP_DURATION]: {
    type: HealthDataType.SLEEP_DURATION,
    icon: Moon,
    label: "睡眠时长",
    unit: "小时",
    category: "sleep",
    color: "#9C27B0",
  },
  [HealthDataType.SLEEP_QUALITY]: {
    type: HealthDataType.SLEEP_QUALITY,
    icon: Moon,
    label: "睡眠质量",
    unit: "分",
    category: "sleep",
    color: "#9C27B0",
  },

  // 心率/HRV
  [HealthDataType.HRV]: {
    type: HealthDataType.HRV,
    icon: Heart,
    label: "心率变异性",
    unit: "ms",
    category: "heart",
    color: "#FF5252",
  },
  [HealthDataType.HEART_RATE_RESTING]: {
    type: HealthDataType.HEART_RATE_RESTING,
    icon: Heart,
    label: "静息心率",
    unit: "bpm",
    category: "heart",
    color: "#FF5252",
  },
  [HealthDataType.HEART_RATE]: {
    type: HealthDataType.HEART_RATE,
    icon: Heart,
    label: "心率",
    unit: "bpm",
    category: "heart",
    color: "#FF5252",
  },

  // 活动
  [HealthDataType.STEPS]: {
    type: HealthDataType.STEPS,
    icon: Activity,
    label: "步数",
    unit: "步",
    category: "activity",
    color: "#4CAF50",
  },
  [HealthDataType.DISTANCE]: {
    type: HealthDataType.DISTANCE,
    icon: Activity,
    label: "距离",
    unit: "公里",
    category: "activity",
    color: "#4CAF50",
  },
  [HealthDataType.ACTIVE_ENERGY]: {
    type: HealthDataType.ACTIVE_ENERGY,
    icon: Zap,
    label: "活动能量",
    unit: "千卡",
    category: "activity",
    color: "#FF9800",
  },
  [HealthDataType.EXERCISE_MINUTES]: {
    type: HealthDataType.EXERCISE_MINUTES,
    icon: Activity,
    label: "运动时长",
    unit: "分钟",
    category: "activity",
    color: "#4CAF50",
  },

  // 主观评估
  [HealthDataType.ENERGY_LEVEL]: {
    type: HealthDataType.ENERGY_LEVEL,
    icon: Zap,
    label: "能量水平",
    unit: "分",
    category: "subjective",
    color: "#FFD700",
  },
  [HealthDataType.MOOD]: {
    type: HealthDataType.MOOD,
    icon: Smile,
    label: "心情",
    unit: "分",
    category: "subjective",
    color: "#FF69B4",
  },
  [HealthDataType.FOCUS]: {
    type: HealthDataType.FOCUS,
    icon: Target,
    label: "专注度",
    unit: "分",
    category: "subjective",
    color: "#00BCD4",
  },

  // 其他生理指标
  [HealthDataType.BLOOD_OXYGEN]: {
    type: HealthDataType.BLOOD_OXYGEN,
    icon: Droplets,
    label: "血氧饱和度",
    unit: "%",
    category: "other",
    color: "#2196F3",
  },
  [HealthDataType.STRESS_LEVEL]: {
    type: HealthDataType.STRESS_LEVEL,
    icon: Brain,
    label: "压力水平",
    unit: "分",
    category: "other",
    color: "#F44336",
  },
  [HealthDataType.RESPIRATORY_RATE]: {
    type: HealthDataType.RESPIRATORY_RATE,
    icon: Wind,
    label: "呼吸频率",
    unit: "次/分钟",
    category: "other",
    color: "#00BCD4",
  },
  [HealthDataType.BODY_TEMPERATURE]: {
    type: HealthDataType.BODY_TEMPERATURE,
    icon: Thermometer,
    label: "体温",
    unit: "°C",
    category: "other",
    color: "#FF5722",
  },
};

const CATEGORIES = [
  { id: "all", label: "全部" },
  { id: "sleep", label: "睡眠" },
  { id: "heart", label: "心率" },
  { id: "activity", label: "活动" },
  { id: "subjective", label: "主观" },
  { id: "other", label: "其他" },
];

interface HealthDataTypeSelectorProps {
  onSelect: (dataType: string, config: DataTypeConfig) => void;
  selectedCategory?: string;
}

export function HealthDataTypeSelector({
  onSelect,
  selectedCategory = "all",
}: HealthDataTypeSelectorProps) {
  const filteredTypes = Object.values(DATA_TYPE_CONFIGS).filter((config) =>
    selectedCategory === "all" ? true : config.category === selectedCategory
  );

  return (
    <div className="grid grid-cols-2 gap-3">
      {filteredTypes.map((config) => {
        const Icon = config.icon;
        return (
          <motion.button
            key={config.type}
            onClick={() => onSelect(config.type, config)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 flex items-center gap-3 hover:bg-white/15 transition-all"
          >
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: `${config.color}20` }}
            >
              <Icon
                className="w-6 h-6"
                style={{ color: config.color }}
                strokeWidth={2}
              />
            </div>
            <div className="flex-1 text-left">
              <div className="text-white font-medium text-sm">
                {config.label}
              </div>
              <div className="text-white/60 text-xs">{config.unit}</div>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}

interface CategoryTabsProps {
  selected: string;
  onSelect: (category: string) => void;
}

export function CategoryTabs({ selected, onSelect }: CategoryTabsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {CATEGORIES.map((category) => (
        <button
          key={category.id}
          onClick={() => onSelect(category.id)}
          className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
            selected === category.id
              ? "bg-white text-[#2B69B6]"
              : "bg-white/10 text-white/80 hover:bg-white/15"
          }`}
        >
          {category.label}
        </button>
      ))}
    </div>
  );
}
