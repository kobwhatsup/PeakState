/**
 * 健康数据通用录入表单
 * 支持数值输入、日期时间选择、数据来源选择
 */

import { useState } from "react";
import { motion } from "motion/react";
import { Calendar, Clock, Save, History } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { useHealthStore } from "../store/healthStore";
import { HealthDataSource } from "../api";
import type { DataTypeConfig } from "./HealthDataTypeSelector";

interface HealthDataFormProps {
  dataType: string;
  config: DataTypeConfig;
  onComplete: () => void;
  onCancel: () => void;
  onViewHistory: () => void;
}

export function HealthDataForm({
  dataType,
  config,
  onComplete,
  onCancel,
  onViewHistory,
}: HealthDataFormProps) {
  const { createData, isLoading } = useHealthStore();
  const [value, setValue] = useState("");
  const [recordedDate, setRecordedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [recordedTime, setRecordedTime] = useState(
    new Date().toTimeString().slice(0, 5)
  );
  const [source, setSource] = useState(HealthDataSource.MANUAL);

  const Icon = config.icon;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!value || parseFloat(value) < 0) {
      alert("请输入有效的数值");
      return;
    }

    const recordedAt = new Date(`${recordedDate}T${recordedTime}`).toISOString();

    const result = await createData({
      data_type: dataType,
      value: parseFloat(value),
      unit: config.unit,
      source,
      recorded_at: recordedAt,
    });

    if (result) {
      // 成功提示
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
      {/* 标题区 */}
      <div className="flex items-center gap-4">
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center"
          style={{ backgroundColor: `${config.color}20` }}
        >
          <Icon
            className="w-8 h-8"
            style={{ color: config.color }}
            strokeWidth={2}
          />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">{config.label}</h2>
          <p className="text-white/60">单位: {config.unit}</p>
        </div>
      </div>

      {/* 表单 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 数值输入 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white text-sm">数值</Label>
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
        </div>

        {/* 日期时间 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white text-sm flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            记录时间
          </Label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Input
                type="date"
                value={recordedDate}
                onChange={(e) => setRecordedDate(e.target.value)}
                className="bg-white/5 border-white/20 text-white"
              />
            </div>
            <div>
              <Input
                type="time"
                value={recordedTime}
                onChange={(e) => setRecordedTime(e.target.value)}
                className="bg-white/5 border-white/20 text-white"
              />
            </div>
          </div>
        </div>

        {/* 数据来源 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white text-sm">数据来源</Label>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value as HealthDataSource)}
            className="w-full bg-white/5 border border-white/20 text-white rounded-xl px-4 py-3"
          >
            <option value={HealthDataSource.MANUAL}>手动输入</option>
            <option value={HealthDataSource.APPLE_HEALTH}>Apple Health</option>
            <option value={HealthDataSource.GOOGLE_FIT}>Google Fit</option>
            <option value={HealthDataSource.OURA_RING}>Oura Ring</option>
            <option value={HealthDataSource.WHOOP}>WHOOP</option>
          </select>
        </div>

        {/* 按钮组 */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            onClick={onViewHistory}
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
