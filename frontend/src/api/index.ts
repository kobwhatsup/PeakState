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

// 类型定义
export type {
  ApiResponse,
  CoachType,
  User,
  RegisterRequest,
  LoginRequest,
  Token,
  Message,
  Conversation,
  SendMessageRequest,
  SendMessageResponse,
  CreateConversationRequest,
  HealthData,
} from "./types";
