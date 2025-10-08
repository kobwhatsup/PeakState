/**
 * EnergyCurveChart Component
 * Displays energy predictions over time using Recharts
 */

import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonSpinner } from '@ionic/react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { EnergyPrediction } from '../../api/energy';

interface EnergyCurveChartProps {
  predictions: EnergyPrediction[];
  isLoading?: boolean;
  error?: string | null;
  title?: string;
  showLegend?: boolean;
  height?: number;
}

const EnergyCurveChart: React.FC<EnergyCurveChartProps> = ({
  predictions,
  isLoading = false,
  error = null,
  title = '精力趋势预测',
  showLegend = true,
  height = 300,
}) => {
  // 格式化时间
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 格式化简短时间（仅小时）
  const formatShortTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 准备图表数据
  const chartData = predictions.map((pred) => ({
    time: pred.timestamp,
    score: pred.score,
    confidence: pred.confidence * 10, // 转换为0-10范围便于显示
    level: pred.energy_level,
  }));

  // 自定义Tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold mb-1">{formatTime(data.time)}</p>
          <p className="text-sm text-gray-700">
            精力分数: <span className="font-bold">{data.score}/10</span>
          </p>
          <p className="text-sm text-gray-700">
            置信度: <span className="font-bold">{(data.confidence * 10).toFixed(0)}%</span>
          </p>
          <p className="text-sm text-gray-700">
            等级:
            <span
              className={`font-bold ml-1 ${
                data.level === 'high'
                  ? 'text-green-600'
                  : data.level === 'medium'
                  ? 'text-yellow-600'
                  : 'text-red-600'
              }`}
            >
              {data.level === 'high' ? '高' : data.level === 'medium' ? '中' : '低'}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <IonCard>
        <IonCardHeader>
          <IonCardTitle>{title}</IonCardTitle>
        </IonCardHeader>
        <IonCardContent className="flex justify-center items-center" style={{ height }}>
          <IonSpinner name="crescent" />
        </IonCardContent>
      </IonCard>
    );
  }

  if (error) {
    return (
      <IonCard color="danger">
        <IonCardHeader>
          <IonCardTitle>{title}</IonCardTitle>
        </IonCardHeader>
        <IonCardContent>
          <p className="text-white">{error}</p>
        </IonCardContent>
      </IonCard>
    );
  }

  if (!predictions || predictions.length === 0) {
    return (
      <IonCard>
        <IonCardHeader>
          <IonCardTitle>{title}</IonCardTitle>
        </IonCardHeader>
        <IonCardContent>
          <p className="text-gray-500">暂无预测数据</p>
        </IonCardContent>
      </IonCard>
    );
  }

  return (
    <IonCard>
      <IonCardHeader>
        <IonCardTitle>{title}</IonCardTitle>
      </IonCardHeader>
      <IonCardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="time"
              tickFormatter={formatShortTime}
              stroke="#666"
              tick={{ fontSize: 12 }}
            />
            <YAxis
              domain={[0, 10]}
              ticks={[0, 2, 4, 6, 8, 10]}
              stroke="#666"
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && (
              <Legend
                wrapperStyle={{ fontSize: '12px' }}
                iconType="line"
              />
            )}

            {/* 参考线 - 标记高中低精力阈值 */}
            <ReferenceLine
              y={7}
              stroke="#10b981"
              strokeDasharray="3 3"
              label={{ value: '高', position: 'right', fontSize: 10 }}
            />
            <ReferenceLine
              y={4}
              stroke="#f59e0b"
              strokeDasharray="3 3"
              label={{ value: '中', position: 'right', fontSize: 10 }}
            />

            {/* 精力分数曲线 */}
            <Line
              type="monotone"
              dataKey="score"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4, fill: '#3b82f6' }}
              activeDot={{ r: 6 }}
              name="精力分数"
            />

            {/* 置信度曲线（可选） */}
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#8b5cf6"
              strokeWidth={1.5}
              strokeDasharray="5 5"
              dot={false}
              name="置信度"
              opacity={0.6}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* 图例说明 */}
        <div className="mt-4 text-xs text-gray-600 space-y-1">
          <p>• 实线：精力分数预测</p>
          <p>• 虚线：预测置信度</p>
          <p>• 绿色线：高精力阈值 (7分)</p>
          <p>• 黄色线：中精力阈值 (4分)</p>
        </div>
      </IonCardContent>
    </IonCard>
  );
};

export default EnergyCurveChart;
