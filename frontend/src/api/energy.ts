/**
 * 精力预测API模块
 * Energy Prediction and Digital Twin APIs
 */

import { apiClient } from "./client";

// ========== Types ==========

export interface EnergyPrediction {
  id?: string;
  timestamp: string;
  energy_level: "high" | "medium" | "low";
  score: number; // 1-10
  confidence: number; // 0-1
  factors: {
    sleep?: number;
    physiology?: number;
    activity?: number;
    time_of_day?: number;
    subjective?: number;
    trend?: number;
    environment?: number;
  };
  recommendations: string[];
}

export interface PersonalBaseline {
  user_id: string;
  avg_energy: number;
  high_threshold: number;
  low_threshold: number;
  optimal_sleep: number;
  last_updated: string;
}

export interface EnergyPattern {
  pattern_type: "daily" | "weekly" | "monthly";
  description: string;
  peak_hours: number[];
  low_hours: number[];
  confidence: number;
}

export interface DigitalTwin {
  user_id: string;
  current_energy: EnergyPrediction | null;
  hourly_predictions: EnergyPrediction[];
  daily_predictions: EnergyPrediction[];
  patterns: EnergyPattern[];
  baseline: PersonalBaseline | null;
  stats: {
    avg_energy_7d: number;
    avg_energy_30d: number;
    avg_sleep_7d: number;
    energy_stability: number;
  };
  recommendations: string[];
  data_completeness: number;
  last_updated: string;
}

export interface ValidationRequest {
  prediction_id: string;
  actual_energy: number; // 1-10
}

export interface ValidationResponse {
  prediction_id: string;
  predicted_energy: number;
  actual_energy: number;
  prediction_error: number;
  message: string;
}

export interface ModelAccuracy {
  total_predictions: number;
  validated_predictions: number;
  validation_rate: number;
  mean_absolute_error: number;
  root_mean_square_error: number;
  accuracy_within_1: number;
  accuracy_within_2: number;
  period_days: number;
}

// ========== API Functions ==========

/**
 * 获取当前精力状态
 */
export const getCurrentEnergy = async (): Promise<EnergyPrediction> => {
  const response = await apiClient.get<EnergyPrediction>("/energy/current");
  return response.data;
};

/**
 * 预测未来精力曲线
 * @param hours 预测小时数，默认24小时
 */
export const predictFutureEnergy = async (
  hours: number = 24
): Promise<EnergyPrediction[]> => {
  const response = await apiClient.get<EnergyPrediction[]>("/energy/predict", {
    params: { hours },
  });
  return response.data;
};

/**
 * 获取精力数字孪生
 * @param includePredictions 是否包含预测曲线
 * @param predictionHours 预测小时数
 */
export const getDigitalTwin = async (
  includePredictions: boolean = true,
  predictionHours: number = 24
): Promise<DigitalTwin> => {
  const response = await apiClient.get<DigitalTwin>("/energy/digital-twin", {
    params: {
      include_predictions: includePredictions,
      prediction_hours: predictionHours,
    },
  });
  return response.data;
};

/**
 * 获取精力模式
 */
export const getEnergyPatterns = async (): Promise<EnergyPattern[]> => {
  const response = await apiClient.get<EnergyPattern[]>("/energy/patterns");
  return response.data;
};

/**
 * 获取个性化基线
 */
export const getPersonalBaseline = async (): Promise<PersonalBaseline> => {
  const response = await apiClient.get<PersonalBaseline>("/energy/baseline");
  return response.data;
};

/**
 * 获取精力统计数据
 */
export const getEnergyStats = async (): Promise<{
  avg_energy_7d: number;
  avg_energy_30d: number;
  avg_sleep_7d: number;
  energy_stability: number;
}> => {
  const response = await apiClient.get("/energy/stats");
  return response.data;
};

/**
 * 验证精力预测
 * @param request 验证请求
 */
export const validatePrediction = async (
  request: ValidationRequest
): Promise<ValidationResponse> => {
  const response = await apiClient.post<ValidationResponse>(
    "/energy/validate-prediction",
    request
  );
  return response.data;
};

/**
 * 获取模型准确性统计
 * @param days 统计周期(天)，默认30天
 */
export const getModelAccuracy = async (
  days: number = 30
): Promise<ModelAccuracy> => {
  const response = await apiClient.get<ModelAccuracy>("/energy/model-accuracy", {
    params: { days },
  });
  return response.data;
};
