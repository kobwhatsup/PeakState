/**
 * 健康数据API
 * 提供健康数据的录入、查询、统计功能
 */

import { apiClient } from "./client";
import type {
  HealthDataCreate,
  HealthDataBatchCreate,
  HealthDataResponse,
  HealthDataListResponse,
  HealthSummaryResponse,
} from "./types";

/**
 * 创建单条健康数据
 */
export const createHealthData = async (
  data: HealthDataCreate
): Promise<HealthDataResponse> => {
  const response = await apiClient.post<HealthDataResponse>("/health/data", data);
  return response.data;
};

/**
 * 批量创建健康数据
 */
export const createHealthDataBatch = async (
  data: HealthDataCreate[]
): Promise<HealthDataResponse[]> => {
  const response = await apiClient.post<HealthDataResponse[]>("/health/data/batch", {
    data,
  });
  return response.data;
};

/**
 * 获取指定类型的健康数据
 */
export const getHealthDataByType = async (
  dataType: string,
  params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }
): Promise<HealthDataListResponse> => {
  const response = await apiClient.get<HealthDataListResponse>(
    `/health/data/${dataType}`,
    { params }
  );
  return response.data;
};

/**
 * 获取最新的健康数据
 */
export const getLatestHealthData = async (
  dataType: string
): Promise<HealthDataResponse> => {
  const response = await apiClient.get<HealthDataResponse>(
    `/health/data/${dataType}/latest`
  );
  return response.data;
};

/**
 * 获取健康数据摘要
 */
export const getHealthSummary = async (
  days: number = 7
): Promise<HealthSummaryResponse> => {
  const response = await apiClient.get<HealthSummaryResponse>("/health/summary", {
    params: { days },
  });
  return response.data;
};

/**
 * 删除健康数据
 */
export const deleteHealthData = async (dataId: string): Promise<void> => {
  await apiClient.delete(`/health/data/${dataId}`);
};
