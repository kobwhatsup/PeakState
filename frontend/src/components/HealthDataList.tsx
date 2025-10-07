/**
 * 健康数据历史列表
 * 显示指定类型的健康数据历史记录
 */

import { useEffect } from "react";
import { motion } from "motion/react";
import { ArrowLeft, Trash2, Calendar } from "lucide-react";
import { Button } from "./ui/button";
import { useHealthStore } from "../store/healthStore";
import { DATA_TYPE_CONFIGS } from "./HealthDataTypeSelector";

interface HealthDataListProps {
  dataType: string;
  onBack: () => void;
}

export function HealthDataList({ dataType, onBack }: HealthDataListProps) {
  const { healthData, loadDataByType, deleteData, isLoading } =
    useHealthStore();
  const config = DATA_TYPE_CONFIGS[dataType];
  const data = healthData[dataType] || [];

  useEffect(() => {
    // 加载最近30天的数据
    loadDataByType(dataType, { limit: 100 });
  }, [dataType, loadDataByType]);

  const handleDelete = async (dataId: string) => {
    if (confirm("确定要删除这条数据吗?")) {
      await deleteData(dataId, dataType);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const dateOnly = date.toLocaleDateString("zh-CN");
    const timeOnly = date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });

    if (date.toDateString() === today.toDateString()) {
      return `今天 ${timeOnly}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      return `昨天 ${timeOnly}`;
    } else {
      return `${dateOnly} ${timeOnly}`;
    }
  };

  const Icon = config?.icon;

  if (!config) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="flex items-center gap-4">
        <Button
          onClick={onBack}
          variant="ghost"
          className="text-white hover:bg-white/10"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div className="flex items-center gap-3">
          {Icon && (
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
          )}
          <div>
            <h2 className="text-xl font-bold text-white">{config.label}历史</h2>
            <p className="text-white/60 text-sm">共 {data.length} 条记录</p>
          </div>
        </div>
      </div>

      {/* 数据列表 */}
      {isLoading ? (
        <div className="text-center text-white/60 py-12">加载中...</div>
      ) : data.length === 0 ? (
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-12 text-center">
          <Calendar className="w-16 h-16 text-white/40 mx-auto mb-4" />
          <p className="text-white/60">暂无数据</p>
          <p className="text-white/40 text-sm mt-2">开始记录您的健康数据吧!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 flex items-center justify-between group hover:bg-white/15 transition-all"
            >
              <div className="flex-1">
                <div className="flex items-baseline gap-3">
                  <span
                    className="text-3xl font-bold"
                    style={{ color: config.color }}
                  >
                    {item.value}
                  </span>
                  <span className="text-white/60">{item.unit || config.unit}</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Calendar className="w-3 h-3 text-white/40" />
                  <span className="text-white/60 text-sm">
                    {formatDate(item.recorded_at)}
                  </span>
                  <span className="text-white/40 text-xs">· {item.source}</span>
                </div>
              </div>

              <Button
                onClick={() => handleDelete(item.id)}
                variant="ghost"
                size="sm"
                className="text-white/40 hover:text-red-400 hover:bg-red-400/10 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
