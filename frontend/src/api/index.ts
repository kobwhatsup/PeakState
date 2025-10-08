/**
 * API导出入口
 * 统一导出所有API接口和类型
 */

// 客户端和工具
export { apiClient, tokenStorage, handleApiError } from "./client";

// 认证接口
export {
  register,
  login,
  logout,
  getCurrentUser,
  updateUser,
  refreshToken,
  isAuthenticated,
} from "./auth";

// 聊天接口
export {
  sendMessage,
  createConversation,
  getConversations,
  getConversationHistory,
  deleteConversation,
  debugRouting,
} from "./chat";

// 健康数据接口
export {
  createHealthData,
  createHealthDataBatch,
  getHealthDataByType,
  getLatestHealthData,
  getHealthSummary,
  deleteHealthData,
} from "./health";

// 天气和环境数据接口
export {
  getCurrentWeather,
  reportEnvironmentData,
  getEnvironmentHistory,
} from "./weather";

// 类型定义
export type {
  ApiResponse,
  CoachType,
  User,
  RegisterRequest,
  LoginRequest,
  UpdateUserRequest,
  Token,
  Message,
  Conversation,
  SendMessageRequest,
  SendMessageResponse,
  CreateConversationRequest,
  HealthData,
  HealthDataCreate,
  HealthDataBatchCreate,
  HealthDataResponse,
  HealthDataListResponse,
  HealthSummaryResponse,
} from "./types";

export { HealthDataType, HealthDataSource } from "./types";

// 天气和环境数据类型
export type {
  WeatherData,
  WeatherRequest,
  EnvironmentReportRequest,
  EnvironmentReportResponse,
} from "./weather";

// 精力预测和数字孪生
export {
  getCurrentEnergy,
  predictFutureEnergy,
  getDigitalTwin,
  getEnergyPatterns,
  getPersonalBaseline,
  getEnergyStats,
  validatePrediction,
  getModelAccuracy,
} from "./energy";

export type {
  EnergyPrediction,
  PersonalBaseline,
  EnergyPattern,
  DigitalTwin,
  ValidationRequest,
  ValidationResponse,
  ModelAccuracy,
} from "./energy";
