/**
 * 健康数据摘要卡片
 * 显示7天/30天的健康数据趋势和统计
 */

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { ArrowLeft, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Button } from "./ui/button";
import { useHealthStore } from "../store/healthStore";
import { DATA_TYPE_CONFIGS } from "./HealthDataTypeSelector";

interface HealthSummaryCardProps {
  onBack: () => void;
}

export function HealthSummaryCard({ onBack }: HealthSummaryCardProps) {
  const { summary, loadSummary, isLoading } = useHealthStore();
  const [period, setPeriod] = useState<7 | 30>(7);

  useEffect(() => {
    loadSummary(period);
  }, [period, loadSummary]);

  const summaryData = summary?.summary || {};
  const summaryEntries = Object.entries(summaryData);

  return (
    <div className="space-y-6">
      {/* 标题和周期选择 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            onClick={onBack}
            variant="ghost"
            className="text-white hover:bg-white/10"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h2 className="text-xl font-bold text-white">健康摘要</h2>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setPeriod(7)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              period === 7
                ? "bg-white text-[#2B69B6]"
                : "bg-white/10 text-white/80 hover:bg-white/15"
            }`}
          >
            7天
          </button>
          <button
            onClick={() => setPeriod(30)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              period === 30
                ? "bg-white text-[#2B69B6]"
                : "bg-white/10 text-white/80 hover:bg-white/15"
            }`}
          >
            30天
          </button>
        </div>
      </div>

      {/* 摘要卡片列表 */}
      {isLoading ? (
        <div className="text-center text-white/60 py-12">加载中...</div>
      ) : summaryEntries.length === 0 ? (
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-12 text-center">
          <p className="text-white/60">暂无数据</p>
          <p className="text-white/40 text-sm mt-2">
            开始记录您的健康数据以查看摘要
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {summaryEntries.map(([dataType, data], index) => {
            const config = DATA_TYPE_CONFIGS[dataType];
            if (!config) return null;

            const Icon = config.icon;
            const avgValue = (data as any).average;

            return (
              <motion.div
                key={dataType}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-xl rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
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
                    <div>
                      <h3 className="text-white font-medium">{config.label}</h3>
                      <p className="text-white/60 text-sm">
                        {period}天平均
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-baseline gap-2">
                  <span
                    className="text-4xl font-bold"
                    style={{ color: config.color }}
                  >
                    {avgValue.toFixed(1)}
                  </span>
                  <span className="text-white/60">{config.unit}</span>
                </div>

                {/* 简化的趋势展示 */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 text-white/60 text-sm">
                    <Minus className="w-4 h-4" />
                    <span>最近{period}天数据</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* 提示信息 */}
      {summaryEntries.length > 0 && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4">
          <p className="text-white/60 text-sm text-center">
            💡 持续记录数据可以更好地了解您的健康趋势
          </p>
        </div>
      )}
    </div>
  );
}
