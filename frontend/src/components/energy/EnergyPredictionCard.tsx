/**
 * EnergyPredictionCard Component
 * Displays current energy level with score, confidence, and recommendations
 */

import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonChip, IonIcon, IonSpinner } from '@ionic/react';
import { flashOutline, batteryHalfOutline, batteryDeadOutline, trendingUpOutline } from 'ionicons/icons';
import type { EnergyPrediction } from '../../api/energy';

interface EnergyPredictionCardProps {
  prediction: EnergyPrediction | null;
  isLoading?: boolean;
  error?: string | null;
  onValidate?: (predictionId: string, actualEnergy: number) => void;
}

const EnergyPredictionCard: React.FC<EnergyPredictionCardProps> = ({
  prediction,
  isLoading = false,
  error = null,
  onValidate,
}) => {
  // 获取精力等级对应的图标
  const getEnergyIcon = (level: string) => {
    switch (level) {
      case 'high':
        return flashOutline;
      case 'medium':
        return batteryHalfOutline;
      case 'low':
        return batteryDeadOutline;
      default:
        return batteryHalfOutline;
    }
  };

  // 获取精力等级对应的颜色
  const getEnergyColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'success';
      case 'medium':
        return 'warning';
      case 'low':
        return 'danger';
      default:
        return 'medium';
    }
  };

  // 获取精力等级文本
  const getEnergyText = (level: string) => {
    switch (level) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return '未知';
    }
  };

  // 格式化时间
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <IonCard>
        <IonCardContent className="flex justify-center items-center py-8">
          <IonSpinner name="crescent" />
        </IonCardContent>
      </IonCard>
    );
  }

  if (error) {
    return (
      <IonCard color="danger">
        <IonCardContent>
          <p className="text-white">{error}</p>
        </IonCardContent>
      </IonCard>
    );
  }

  if (!prediction) {
    return (
      <IonCard>
        <IonCardContent>
          <p className="text-gray-500">暂无精力数据</p>
        </IonCardContent>
      </IonCard>
    );
  }

  return (
    <IonCard>
      <IonCardHeader>
        <div className="flex justify-between items-center">
          <IonCardTitle>当前精力状态</IonCardTitle>
          <IonChip color={getEnergyColor(prediction.energy_level)}>
            <IonIcon icon={getEnergyIcon(prediction.energy_level)} />
            <span className="ml-1">{getEnergyText(prediction.energy_level)}</span>
          </IonChip>
        </div>
      </IonCardHeader>

      <IonCardContent>
        {/* 精力分数 */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">精力分数</span>
            <span className="text-2xl font-bold">{prediction.score}/10</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                prediction.energy_level === 'high'
                  ? 'bg-green-500'
                  : prediction.energy_level === 'medium'
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${(prediction.score / 10) * 100}%` }}
            />
          </div>
        </div>

        {/* 置信度 */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">预测置信度</span>
            <span className="text-sm font-medium">
              {(prediction.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500"
              style={{ width: `${prediction.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* 影响因素 */}
        {prediction.factors && Object.keys(prediction.factors).length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">影响因素</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(prediction.factors).map(([key, value]) => (
                <IonChip key={key} outline>
                  <span className="text-xs">
                    {key}: {typeof value === 'number' ? value.toFixed(1) : value}
                  </span>
                </IonChip>
              ))}
            </div>
          </div>
        )}

        {/* 建议 */}
        {prediction.recommendations && prediction.recommendations.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2 flex items-center">
              <IonIcon icon={trendingUpOutline} className="mr-1" />
              优化建议
            </h4>
            <ul className="list-disc list-inside space-y-1">
              {prediction.recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 时间戳 */}
        <div className="text-xs text-gray-500 text-right">
          {formatTimestamp(prediction.timestamp)}
        </div>
      </IonCardContent>
    </IonCard>
  );
};

export default EnergyPredictionCard;
