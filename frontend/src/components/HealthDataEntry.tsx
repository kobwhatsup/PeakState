/**
 * 健康数据录入主界面
 * 提供数据录入、查看和管理功能
 */

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ArrowLeft, Plus, BarChart3 } from "lucide-react";
import { Button } from "./ui/button";
import {
  HealthDataTypeSelector,
  CategoryTabs,
  DATA_TYPE_CONFIGS,
} from "./HealthDataTypeSelector";
import { HealthDataForm } from "./HealthDataForm";
import { SubjectiveForm } from "./SubjectiveForm";
import { SleepDataForm } from "./SleepDataForm";
import { ActivityForm } from "./ActivityForm";
import { HeartRateForm } from "./HeartRateForm";
import { HealthDataList } from "./HealthDataList";
import { HealthSummaryCard } from "./HealthSummaryCard";

type ViewMode = "selector" | "form" | "list" | "summary";

interface HealthDataEntryProps {
  onBack: () => void;
}

export function HealthDataEntry({ onBack }: HealthDataEntryProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("selector");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDataType, setSelectedDataType] = useState<string | null>(null);

  const handleTypeSelect = (dataType: string) => {
    setSelectedDataType(dataType);
    setViewMode("form");
  };

  const handleFormComplete = () => {
    setViewMode("selector");
    setSelectedDataType(null);
  };

  const handleViewList = (dataType: string) => {
    setSelectedDataType(dataType);
    setViewMode("list");
  };

  const selectedConfig = selectedDataType
    ? DATA_TYPE_CONFIGS[selectedDataType]
    : null;

  return (
    <div className="h-screen flex flex-col relative overflow-hidden safe-area-top safe-area-bottom">
      {/* 背景装饰 - 与应用统一 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-[800px] h-[800px] rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 60%)",
            top: "-20%",
            left: "50%",
            transform: "translateX(-50%)",
            filter: "blur(100px)",
          }}
        />
        <div
          className="absolute w-[600px] h-[600px] rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(77, 208, 225, 0.08) 0%, transparent 70%)",
            bottom: "-10%",
            right: "-10%",
            filter: "blur(80px)",
          }}
        />
      </div>

      {/* 顶部导航栏 */}
      <div className="relative z-10 px-4 sm:px-5 lg:px-6 pt-6 sm:pt-7 lg:pt-8 pb-3 sm:pb-4">
        <div className="flex items-center justify-between">
          <Button
            onClick={onBack}
            variant="ghost"
            className="text-white hover:bg-white/10 touch-target"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>

          <h1 className="text-lg sm:text-xl font-semibold text-white">健康数据</h1>

          <Button
            onClick={() => setViewMode("summary")}
            variant="ghost"
            className="text-white hover:bg-white/10 touch-target"
          >
            <BarChart3 className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="relative z-10 flex-1 px-4 sm:px-5 lg:px-6 pb-4 sm:pb-5 lg:pb-6 overflow-y-auto">
        <AnimatePresence mode="wait">
          {/* 类型选择器视图 */}
          {viewMode === "selector" && (
            <motion.div
              key="selector"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <CategoryTabs
                selected={selectedCategory}
                onSelect={setSelectedCategory}
              />

              <HealthDataTypeSelector
                selectedCategory={selectedCategory}
                onSelect={handleTypeSelect}
              />
            </motion.div>
          )}

          {/* 数据录入表单视图 - 智能路由到专项表单 */}
          {viewMode === "form" && selectedConfig && (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              {selectedConfig.category === "subjective" ? (
                <SubjectiveForm
                  onComplete={handleFormComplete}
                  onCancel={() => setViewMode("selector")}
                  onViewHistory={handleViewList}
                />
              ) : selectedConfig.category === "sleep" ? (
                <SleepDataForm
                  onComplete={handleFormComplete}
                  onCancel={() => setViewMode("selector")}
                  onViewHistory={handleViewList}
                />
              ) : selectedConfig.category === "activity" ? (
                <ActivityForm
                  onComplete={handleFormComplete}
                  onCancel={() => setViewMode("selector")}
                  onViewHistory={handleViewList}
                />
              ) : selectedConfig.category === "heart" ? (
                <HeartRateForm
                  onComplete={handleFormComplete}
                  onCancel={() => setViewMode("selector")}
                  onViewHistory={handleViewList}
                />
              ) : (
                <HealthDataForm
                  dataType={selectedConfig.type}
                  config={selectedConfig}
                  onComplete={handleFormComplete}
                  onCancel={() => setViewMode("selector")}
                  onViewHistory={() => handleViewList(selectedConfig.type)}
                />
              )}
            </motion.div>
          )}

          {/* 数据列表视图 */}
          {viewMode === "list" && selectedDataType && (
            <motion.div
              key="list"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <HealthDataList
                dataType={selectedDataType}
                onBack={() => setViewMode("form")}
              />
            </motion.div>
          )}

          {/* 健康摘要视图 */}
          {viewMode === "summary" && (
            <motion.div
              key="summary"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <HealthSummaryCard onBack={() => setViewMode("selector")} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
