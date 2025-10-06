/**
 * 认证状态管理
 * 使用Zustand管理用户登录状态和用户信息
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, RegisterRequest, LoginRequest, CoachType } from "../api";
import {
  register as apiRegister,
  login as apiLogin,
  logout as apiLogout,
  getCurrentUser as apiGetCurrentUser,
  isAuthenticated as apiIsAuthenticated,
} from "../api";

interface AuthState {
  // 状态
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // 动作
  register: (data: RegisterRequest) => Promise<void>;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
  updateCoachSelection: (coachType: CoachType) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      isLoading: false,
      error: null,
      isAuthenticated: apiIsAuthenticated(),

      // 用户注册
      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          await apiRegister(data);
          // 注册成功后自动获取用户信息
          await get().fetchCurrentUser();
          set({ isAuthenticated: true });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            "注册失败";
          set({ error: errorMessage, isAuthenticated: false });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // 用户登录
      login: async (data: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          await apiLogin(data);
          // 登录成功后自动获取用户信息
          await get().fetchCurrentUser();
          set({ isAuthenticated: true });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            "登录失败";
          set({ error: errorMessage, isAuthenticated: false });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // 用户退出
      logout: async () => {
        set({ isLoading: true });
        try {
          await apiLogout();
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          });
        } catch (error: any) {
          console.error("Logout error:", error);
          // 即使出错也清除本地状态
          set({
            user: null,
            isAuthenticated: false,
          });
        } finally {
          set({ isLoading: false });
        }
      },

      // 获取当前用户信息
      fetchCurrentUser: async () => {
        if (!apiIsAuthenticated()) {
          set({ user: null, isAuthenticated: false });
          return;
        }

        set({ isLoading: true, error: null });
        try {
          const user = await apiGetCurrentUser();
          set({ user, isAuthenticated: true });
        } catch (error: any) {
          console.error("Fetch user error:", error);
          if (error.response?.status === 401) {
            // Token无效，清除认证状态
            set({
              user: null,
              isAuthenticated: false,
            });
          }
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            "获取用户信息失败";
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // 清除错误
      clearError: () => {
        set({ error: null });
      },

      // 更新教练选择（仅本地状态，实际需要调用API）
      updateCoachSelection: (coachType: CoachType) => {
        const { user } = get();
        if (user) {
          set({
            user: {
              ...user,
              coach_selection: coachType,
            },
          });
        }
      },
    }),
    {
      name: "peakstate-auth", // localStorage key
      partialize: (state) => ({
        // 只持久化用户信息，不持久化loading和error状态
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// 自动初始化：应用启动时尝试获取用户信息
if (apiIsAuthenticated()) {
  useAuthStore.getState().fetchCurrentUser();
}
