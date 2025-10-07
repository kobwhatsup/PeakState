/**
 * 健康数据状态管理
 * 使用Zustand管理健康数据的录入、查询和统计
 */

import { create } from "zustand";
import {
  createHealthData,
  createHealthDataBatch,
  getHealthDataByType,
  getLatestHealthData,
  getHealthSummary,
  deleteHealthData,
  handleApiError,
} from "../api";
import type {
  HealthDataCreate,
  HealthDataResponse,
  HealthDataListResponse,
  HealthSummaryResponse,
} from "../api";

interface HealthStore {
  // 状态
  healthData: Record<string, HealthDataResponse[]>; // 按类型存储的健康数据
  summary: HealthSummaryResponse | null; // 健康摘要
  isLoading: boolean;
  error: string | null;

  // 操作
  createData: (data: HealthDataCreate) => Promise<HealthDataResponse | null>;
  createBatch: (data: HealthDataCreate[]) => Promise<HealthDataResponse[] | null>;
  loadDataByType: (
    dataType: string,
    params?: { start_date?: string; end_date?: string; limit?: number }
  ) => Promise<void>;
  loadLatest: (dataType: string) => Promise<HealthDataResponse | null>;
  loadSummary: (days?: number) => Promise<void>;
  deleteData: (dataId: string, dataType: string) => Promise<boolean>;
  clearError: () => void;
  reset: () => void;
}

export const useHealthStore = create<HealthStore>((set, get) => ({
  // 初始状态
  healthData: {},
  summary: null,
  isLoading: false,
  error: null,

  // 创建单条健康数据
  createData: async (data: HealthDataCreate) => {
    set({ isLoading: true, error: null });
    try {
      const response = await createHealthData(data);

      // 更新本地状态
      const { healthData } = get();
      const dataType = data.data_type;
      const existingData = healthData[dataType] || [];

      set({
        healthData: {
          ...healthData,
          [dataType]: [response, ...existingData],
        },
        isLoading: false,
      });

      return response;
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
      return null;
    }
  },

  // 批量创建健康数据
  createBatch: async (data: HealthDataCreate[]) => {
    set({ isLoading: true, error: null });
    try {
      const responses = await createHealthDataBatch(data);

      // 按类型分组更新本地状态
      const { healthData } = get();
      const newHealthData = { ...healthData };

      responses.forEach((response) => {
        const dataType = response.data_type;
        const existingData = newHealthData[dataType] || [];
        newHealthData[dataType] = [response, ...existingData];
      });

      set({ healthData: newHealthData, isLoading: false });
      return responses;
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
      return null;
    }
  },

  // 加载指定类型的健康数据
  loadDataByType: async (dataType, params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await getHealthDataByType(dataType, params);

      const { healthData } = get();
      set({
        healthData: {
          ...healthData,
          [dataType]: response.data,
        },
        isLoading: false,
      });
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
    }
  },

  // 加载最新数据
  loadLatest: async (dataType: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await getLatestHealthData(dataType);
      set({ isLoading: false });
      return response;
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
      return null;
    }
  },

  // 加载健康摘要
  loadSummary: async (days = 7) => {
    set({ isLoading: true, error: null });
    try {
      const response = await getHealthSummary(days);
      set({ summary: response, isLoading: false });
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
    }
  },

  // 删除健康数据
  deleteData: async (dataId: string, dataType: string) => {
    set({ isLoading: true, error: null });
    try {
      await deleteHealthData(dataId);

      // 从本地状态中移除
      const { healthData } = get();
      const existingData = healthData[dataType] || [];
      const filteredData = existingData.filter((item) => item.id !== dataId);

      set({
        healthData: {
          ...healthData,
          [dataType]: filteredData,
        },
        isLoading: false,
      });

      return true;
    } catch (error) {
      const errorMessage = handleApiError(error);
      set({ error: errorMessage, isLoading: false });
      return false;
    }
  },

  // 清除错误
  clearError: () => set({ error: null }),

  // 重置状态
  reset: () =>
    set({
      healthData: {},
      summary: null,
      isLoading: false,
      error: null,
    }),
}));
