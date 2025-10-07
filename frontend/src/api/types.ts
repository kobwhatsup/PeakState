/**
 * API类型定义
 * 与后端API响应结构保持一致
 */

// ========== 通用类型 ==========

export interface ApiResponse<T = any> {
  success?: boolean;
  message?: string;
  data?: T;
  errors?: any[];
}

// ========== 用户相关 ==========

export type CoachType = "sage" | "companion" | "expert";

export interface User {
  id: string;
  phone_number: string;
  coach_selection: CoachType;
  timezone: string;
  is_subscribed: boolean;
  subscription_type: string | null;
  subscription_end_date: string | null;
  is_trial: boolean;
  trial_end_date: string | null;
  morning_briefing_enabled: boolean;
  morning_briefing_time: string;
  evening_review_enabled: boolean;
  evening_review_time: string;
  created_at: string;
  last_login_at: string | null;
}

export interface RegisterRequest {
  phone_number: string;
  password: string;
  coach_selection: CoachType;
}

export interface LoginRequest {
  phone_number: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ========== 对话相关 ==========

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  tokens_used?: number;
  model_used?: string;
  cost?: number;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_at: string | null;
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  message: Message;
}

export interface CreateConversationRequest {
  title?: string;
}

// ========== 健康数据 ==========

/**
 * 健康数据类型枚举
 */
export enum HealthDataType {
  // 睡眠数据
  SLEEP_DURATION = "sleep_duration",
  SLEEP_QUALITY = "sleep_quality",
  SLEEP_DEEP = "sleep_deep",
  SLEEP_REM = "sleep_rem",
  SLEEP_LIGHT = "sleep_light",

  // 心率变异性
  HRV = "hrv",
  HRV_RMSSD = "hrv_rmssd",
  HRV_SDNN = "hrv_sdnn",

  // 心率
  HEART_RATE = "heart_rate",
  HEART_RATE_RESTING = "heart_rate_resting",
  HEART_RATE_WALKING = "heart_rate_walking",

  // 活动数据
  STEPS = "steps",
  DISTANCE = "distance",
  ACTIVE_ENERGY = "active_energy",
  EXERCISE_MINUTES = "exercise_minutes",

  // 血氧
  BLOOD_OXYGEN = "blood_oxygen",

  // 压力
  STRESS_LEVEL = "stress_level",

  // 呼吸
  RESPIRATORY_RATE = "respiratory_rate",

  // 体温
  BODY_TEMPERATURE = "body_temperature",

  // 主观评估
  ENERGY_LEVEL = "energy_level",
  MOOD = "mood",
  FOCUS = "focus",
}

/**
 * 健康数据来源
 */
export enum HealthDataSource {
  APPLE_HEALTH = "apple_health",
  GOOGLE_FIT = "google_fit",
  OURA_RING = "oura_ring",
  WHOOP = "whoop",
  MANUAL = "manual",
  CALCULATED = "calculated",
}

/**
 * 健康数据创建请求
 */
export interface HealthDataCreate {
  data_type: string;
  value: number;
  source?: string;
  unit?: string;
  recorded_at?: string;
  extra_data?: Record<string, any>;
  external_id?: string;
}

/**
 * 健康数据批量创建请求
 */
export interface HealthDataBatchCreate {
  data: HealthDataCreate[];
}

/**
 * 健康数据响应
 */
export interface HealthDataResponse {
  id: string;
  user_id: string;
  data_type: string;
  value: number;
  unit: string | null;
  source: string;
  recorded_at: string;
  extra_data: Record<string, any> | null;
  created_at: string;
}

/**
 * 健康数据列表响应
 */
export interface HealthDataListResponse {
  data: HealthDataResponse[];
  total: number;
  data_type: string;
}

/**
 * 健康数据摘要响应
 */
export interface HealthSummaryResponse {
  user_id: string;
  period_days: number;
  summary: Record<string, {
    average: number;
    period_days: number;
  }>;
  generated_at: string;
}

export interface HealthData {
  id: string;
  data_type: string;
  source: string;
  value: number;
  unit: string;
  recorded_at: string;
  quality_score: number | null;
  is_anomaly: boolean;
}
