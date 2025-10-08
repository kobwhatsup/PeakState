/**
 * 天气数据API
 * 通过后端代理获取天气信息，保护API密钥安全
 */

import { apiClient } from './client';

export interface WeatherData {
  temperature: number;
  feels_like: number;
  weather: string;
  weather_code: number;
  pressure: number;
  humidity: number;
  air_quality?: number;
  wind_speed: number;
  clouds: number;
  visibility?: number;
  location: string;
  timestamp: string;
}

export interface WeatherRequest {
  latitude: number;
  longitude: number;
}

export interface EnvironmentReportRequest {
  temperature: number;
  weather: string;
  pressure: number;
  humidity: number;
  air_quality?: number;
  location: string;
}

export interface EnvironmentReportResponse {
  id: string;
  user_id: string;
  temperature: number;
  weather: string;
  pressure: number;
  humidity: number;
  air_quality?: number;
  location: string;
  recorded_at: string;
}

/**
 * 获取当前位置的天气数据
 *
 * @param request - 包含经纬度的请求
 * @returns 天气数据
 */
export const getCurrentWeather = async (
  request: WeatherRequest
): Promise<WeatherData> => {
  try {
    const response = await apiClient.post<WeatherData>('/weather/current', request);
    return response.data;
  } catch (error) {
    console.error('[Weather API] Get current weather failed:', error);
    throw error;
  }
};

/**
 * 上报环境数据到后端
 * 用于存储和精力预测分析
 *
 * @param data - 环境数据
 * @returns 上报确认信息
 */
export const reportEnvironmentData = async (
  data: EnvironmentReportRequest
): Promise<EnvironmentReportResponse> => {
  try {
    const response = await apiClient.post<EnvironmentReportResponse>(
      '/environment/report',
      data
    );
    return response.data;
  } catch (error) {
    console.error('[Weather API] Report environment data failed:', error);
    throw error;
  }
};

/**
 * 获取用户的历史环境数据
 *
 * @param hours - 获取最近多少小时的数据，默认24小时
 * @returns 环境数据列表
 */
export const getEnvironmentHistory = async (
  hours: number = 24
): Promise<EnvironmentReportResponse[]> => {
  try {
    const response = await apiClient.get<EnvironmentReportResponse[]>(
      '/environment/history',
      { params: { hours } }
    );
    return response.data;
  } catch (error) {
    console.error('[Weather API] Get environment history failed:', error);
    throw error;
  }
};
