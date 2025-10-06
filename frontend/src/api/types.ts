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
