/**
 * 睡眠数据专项表单
 * 支持睡眠时长、质量及各阶段的批量录入
 */

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Moon, Save, History, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Slider } from "./ui/slider";
import { useHealthStore } from "../store/healthStore";
import { HealthDataType, HealthDataSource } from "../api";

interface SleepDataFormProps {
  onComplete: () => void;
  onCancel: () => void;
  onViewHistory: (dataType: string) => void;
}

export function SleepDataForm({
  onComplete,
  onCancel,
  onViewHistory,
}: SleepDataFormProps) {
  const { createBatch, isLoading } = useHealthStore();

  // 睡眠时间
  const [bedTime, setBedTime] = useState("22:00");
  const [wakeTime, setWakeTime] = useState("07:00");
  const [sleepDuration, setSleepDuration] = useState(9.0);

  // 睡眠质量 (1-10分,可选)
  const [quality, setQuality] = useState([7]);
  const [includeQuality, setIncludeQuality] = useState(true);

  // 睡眠阶段 (可选展开)
  const [showStages, setShowStages] = useState(false);
  const [deepSleep, setDeepSleep] = useState([30]); // 百分比
  const [remSleep, setRemSleep] = useState([25]); // 百分比
  const [lightSleep, setLightSleep] = useState([45]); // 百分比

  // 记录日期
  const [recordedDate, setRecordedDate] = useState(
    new Date().toISOString().split("T")[0]
  );

  // 自动计算睡眠时长
  useEffect(() => {
    const [bedHour, bedMin] = bedTime.split(":").map(Number);
    const [wakeHour, wakeMin] = wakeTime.split(":").map(Number);

    let bedTimeMinutes = bedHour * 60 + bedMin;
    let wakeTimeMinutes = wakeHour * 60 + wakeMin;

    // 跨天处理
    if (wakeTimeMinutes <= bedTimeMinutes) {
      wakeTimeMinutes += 24 * 60;
    }

    const durationMinutes = wakeTimeMinutes - bedTimeMinutes;
    const durationHours = durationMinutes / 60;

    setSleepDuration(Math.round(durationHours * 10) / 10);
  }, [bedTime, wakeTime]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (sleepDuration <= 0) {
      alert("睡眠时长必须大于0");
      return;
    }

    // 构建睡眠时间 (入睡时间为前一天)
    const sleepDate = new Date(recordedDate);
    const [bedHour, bedMin] = bedTime.split(":").map(Number);

    // 如果入睡时间晚于起床时间,认为入睡在前一天
    const [wakeHour] = wakeTime.split(":").map(Number);
    if (bedHour > wakeHour || (bedHour === wakeHour && bedMin > 0)) {
      sleepDate.setDate(sleepDate.getDate() - 1);
    }

    sleepDate.setHours(bedHour, bedMin, 0, 0);
    const recordedAt = sleepDate.toISOString();

    // 批量数据
    const batchData: any[] = [
      {
        data_type: HealthDataType.SLEEP_DURATION,
        value: sleepDuration,
        unit: "小时",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      },
    ];

    // 添加睡眠质量
    if (includeQuality) {
      batchData.push({
        data_type: HealthDataType.SLEEP_QUALITY,
        value: quality[0],
        unit: "分",
        source: HealthDataSource.MANUAL,
        recorded_at: recordedAt,
      });
    }

    // 添加睡眠阶段
    if (showStages) {
      const deepHours = (sleepDuration * deepSleep[0]) / 100;
      const remHours = (sleepDuration * remSleep[0]) / 100;
      const lightHours = (sleepDuration * lightSleep[0]) / 100;

      batchData.push(
        {
          data_type: HealthDataType.SLEEP_DEEP,
          value: Math.round(deepHours * 10) / 10,
          unit: "小时",
          source: HealthDataSource.MANUAL,
          recorded_at: recordedAt,
        },
        {
          data_type: HealthDataType.SLEEP_REM,
          value: Math.round(remHours * 10) / 10,
          unit: "小时",
          source: HealthDataSource.MANUAL,
          recorded_at: recordedAt,
        },
        {
          data_type: HealthDataType.SLEEP_LIGHT,
          value: Math.round(lightHours * 10) / 10,
          unit: "小时",
          source: HealthDataSource.MANUAL,
          recorded_at: recordedAt,
        }
      );
    }

    const result = await createBatch(batchData);

    if (result) {
      alert(`睡眠数据录入成功! 共保存${batchData.length}条记录`);
      onComplete();
    }
  };

  // 睡眠质量快捷选择
  const qualityOptions = [
    { emoji: "😴", label: "差", value: 3 },
    { emoji: "😐", label: "一般", value: 5 },
    { emoji: "😊", label: "良好", value: 7 },
    { emoji: "🌟", label: "优秀", value: 9 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* 标题 */}
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-[#9C27B0]/20 flex items-center justify-center">
          <Moon className="w-8 h-8 text-[#9C27B0]" strokeWidth={2} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">睡眠数据</h2>
          <p className="text-white/60">批量记录睡眠信息</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 睡眠时间 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white font-medium">睡眠时间</Label>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-white/60 text-sm mb-2 block">
                入睡时间
              </Label>
              <Input
                type="time"
                value={bedTime}
                onChange={(e) => setBedTime(e.target.value)}
                className="bg-white/5 border-white/20 text-white text-lg"
              />
            </div>
            <div>
              <Label className="text-white/60 text-sm mb-2 block">
                起床时间
              </Label>
              <Input
                type="time"
                value={wakeTime}
                onChange={(e) => setWakeTime(e.target.value)}
                className="bg-white/5 border-white/20 text-white text-lg"
              />
            </div>
          </div>

          {/* 时间轴可视化 */}
          <div className="bg-white/5 rounded-xl p-4 mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white/60 text-sm">{bedTime}</span>
              <div className="flex-1 mx-4 h-1 bg-gradient-to-r from-[#9C27B0] to-[#E1BEE7] rounded-full" />
              <span className="text-white/60 text-sm">{wakeTime}</span>
            </div>
            <div className="text-center">
              <span className="text-white text-2xl font-bold">
                {sleepDuration}
              </span>
              <span className="text-white/60 ml-2">小时</span>
            </div>
          </div>
        </div>

        {/* 记录日期 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <Label className="text-white text-sm">起床日期</Label>
          <Input
            type="date"
            value={recordedDate}
            onChange={(e) => setRecordedDate(e.target.value)}
            className="bg-white/5 border-white/20 text-white"
          />
          <p className="text-white/40 text-xs">
            系统会自动计算入睡时间为前一天
          </p>
        </div>

        {/* 睡眠质量 */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-white font-medium">睡眠质量 (可选)</Label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={includeQuality}
                onChange={(e) => setIncludeQuality(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-white/60 text-sm">包含</span>
            </label>
          </div>

          {includeQuality && (
            <>
              <div className="grid grid-cols-4 gap-2">
                {qualityOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setQuality([option.value])}
                    className={`bg-white/5 hover:bg-white/15 rounded-xl p-3 transition-all text-center ${
                      quality[0] === option.value ? "ring-2 ring-white/50" : ""
                    }`}
                  >
                    <div className="text-3xl mb-1">{option.emoji}</div>
                    <div className="text-white text-xs">{option.label}</div>
                  </button>
                ))}
              </div>

              <div className="text-center text-white">
                当前: <span className="font-bold text-lg">{quality[0]}</span> 分
              </div>

              <Slider
                value={quality}
                onValueChange={setQuality}
                min={1}
                max={10}
                step={1}
                className="py-2"
              />
            </>
          )}
        </div>

        {/* 睡眠阶段 (可展开) */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 space-y-4">
          <button
            type="button"
            onClick={() => setShowStages(!showStages)}
            className="w-full flex items-center justify-between text-white hover:text-white/80 transition-colors"
          >
            <Label className="font-medium cursor-pointer">
              睡眠阶段分配 (可选)
            </Label>
            {showStages ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </button>

          {showStages && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="space-y-4 pt-2"
            >
              {/* 深睡 */}
              <div>
                <div className="flex justify-between mb-2">
                  <Label className="text-white/80 text-sm">深睡</Label>
                  <span className="text-white/60 text-sm">
                    {deepSleep[0]}% (
                    {((sleepDuration * deepSleep[0]) / 100).toFixed(1)}小时)
                  </span>
                </div>
                <Slider
                  value={deepSleep}
                  onValueChange={setDeepSleep}
                  min={0}
                  max={100}
                  step={5}
                />
              </div>

              {/* REM睡眠 */}
              <div>
                <div className="flex justify-between mb-2">
                  <Label className="text-white/80 text-sm">REM睡眠</Label>
                  <span className="text-white/60 text-sm">
                    {remSleep[0]}% (
                    {((sleepDuration * remSleep[0]) / 100).toFixed(1)}小时)
                  </span>
                </div>
                <Slider
                  value={remSleep}
                  onValueChange={setRemSleep}
                  min={0}
                  max={100}
                  step={5}
                />
              </div>

              {/* 浅睡 */}
              <div>
                <div className="flex justify-between mb-2">
                  <Label className="text-white/80 text-sm">浅睡</Label>
                  <span className="text-white/60 text-sm">
                    {lightSleep[0]}% (
                    {((sleepDuration * lightSleep[0]) / 100).toFixed(1)}小时)
                  </span>
                </div>
                <Slider
                  value={lightSleep}
                  onValueChange={setLightSleep}
                  min={0}
                  max={100}
                  step={5}
                />
              </div>

              <p className="text-white/40 text-xs text-center">
                💡 百分比总和不限制,系统会按比例存储
              </p>
            </motion.div>
          )}
        </div>

        {/* 按钮组 */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            onClick={() => onViewHistory(HealthDataType.SLEEP_DURATION)}
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
            {isLoading ? "保存中..." : "保存睡眠数据"}
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
