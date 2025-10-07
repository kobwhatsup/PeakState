/**
 * Axios HTTP客户端配置
 * 包含请求/响应拦截器，自动处理token刷新
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import type { ApiResponse } from "./types";

// API基础URL - 从环境变量读取，默认localhost:8000
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// 创建axios实例
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Token存储key
const ACCESS_TOKEN_KEY = "peakstate_access_token";
const REFRESH_TOKEN_KEY = "peakstate_refresh_token";

// ========== Token管理 ==========

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },
  clearTokens: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

// ========== 请求拦截器 ==========

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 自动添加token
    const token = tokenStorage.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// ========== 响应拦截器 ==========

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any = null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => {
    // 成功响应直接返回
    return response;
  },
  async (error: AxiosError<ApiResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // 401错误 - token过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 如果正在刷新，将请求加入队列
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        // 没有refresh token，跳转登录
        tokenStorage.clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        // 调用refresh token接口
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token: new_refresh_token } =
          response.data;

        // 保存新token
        tokenStorage.setTokens(access_token, new_refresh_token);

        // 处理队列中的请求
        processQueue(null, access_token);

        // 重试原请求
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // refresh失败，清除token并跳转登录
        processQueue(refreshError, null);
        tokenStorage.clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ========== 错误处理辅助函数 ==========

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const apiError = error as AxiosError<ApiResponse>;

    // 服务器返回的错误信息
    if (apiError.response?.data) {
      const data = apiError.response.data;
      if (data.message) return data.message;
      if (data.detail) return String(data.detail);
      if (data.errors && data.errors.length > 0) {
        return data.errors.map((e: any) => e.msg || e).join(", ");
      }
    }

    // HTTP状态码错误
    if (apiError.response?.status) {
      const status = apiError.response.status;
      switch (status) {
        case 400:
          return "请求参数错误";
        case 401:
          return "未授权，请重新登录";
        case 403:
          return "没有权限访问";
        case 404:
          return "请求的资源不存在";
        case 500:
          return "服务器内部错误";
        case 502:
          return "网关错误";
        case 503:
          return "服务暂时不可用";
        default:
          return `请求失败 (${status})`;
      }
    }

    // 网络错误
    if (apiError.message === "Network Error") {
      return "网络连接失败，请检查网络";
    }

    // 超时
    if (apiError.code === "ECONNABORTED") {
      return "请求超时，请稍后重试";
    }

    return apiError.message || "未知错误";
  }

  // 非axios错误
  if (error instanceof Error) {
    return error.message;
  }

  return "未知错误";
};
