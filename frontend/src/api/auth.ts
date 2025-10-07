/**
 * 认证API接口
 * 用户注册、登录、令牌刷新、获取用户信息
 */

import { apiClient, tokenStorage } from "./client";
import type {
  RegisterRequest,
  LoginRequest,
  Token,
  User,
} from "./types";

// ========== 用户注册 ==========

export const register = async (data: RegisterRequest): Promise<Token> => {
  const response = await apiClient.post<Token>("/auth/register", data);

  // 自动保存token
  if (response.data.access_token && response.data.refresh_token) {
    tokenStorage.setTokens(
      response.data.access_token,
      response.data.refresh_token
    );
  }

  return response.data;
};

// ========== 用户登录 ==========

export const login = async (data: LoginRequest): Promise<Token> => {
  const response = await apiClient.post<Token>("/auth/login", data);

  // 自动保存token
  if (response.data.access_token && response.data.refresh_token) {
    tokenStorage.setTokens(
      response.data.access_token,
      response.data.refresh_token
    );
  }

  return response.data;
};

// ========== 退出登录 ==========

export const logout = async (): Promise<void> => {
  // 清除本地token
  tokenStorage.clearTokens();

  // 可选：调用后端登出接口（如果有）
  // await apiClient.post("/auth/logout");
};

// ========== 获取当前用户信息 ==========

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
};

// ========== 刷新令牌 ==========

export const refreshToken = async (refresh_token: string): Promise<Token> => {
  const response = await apiClient.post<Token>("/auth/refresh", {
    refresh_token,
  });

  // 自动保存新token
  if (response.data.access_token && response.data.refresh_token) {
    tokenStorage.setTokens(
      response.data.access_token,
      response.data.refresh_token
    );
  }

  return response.data;
};

// ========== 检查是否已登录 ==========

export const isAuthenticated = (): boolean => {
  return !!tokenStorage.getAccessToken();
};
