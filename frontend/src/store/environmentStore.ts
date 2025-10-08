/**
 * 环境数据Store
 * 使用Zustand管理位置、天气等环境数据状态
 */

import { create } from 'zustand';
import { getCurrentLocation, LocationCoordinates, LocationError } from '../services/location';
import { getCurrentWeather, reportEnvironmentData, WeatherData } from '../api/weather';

interface EnvironmentState {
  // 位置数据
  location: LocationCoordinates | null;
  locationError: LocationError | null;
  locationLoading: boolean;
  locationPermissionDenied: boolean;

  // 天气数据
  weather: WeatherData | null;
  weatherError: string | null;
  weatherLoading: boolean;

  // 缓存控制
  lastUpdated: number | null;
  cacheMinutes: number; // 缓存有效期（分钟）

  // Actions
  fetchLocation: () => Promise<void>;
  fetchWeather: (forceRefresh?: boolean) => Promise<void>;
  fetchAll: (forceRefresh?: boolean) => Promise<void>;
  clearData: () => void;
  setLocationPermissionDenied: (denied: boolean) => void;
}

const CACHE_DURATION_MS = 30 * 60 * 1000; // 30分钟缓存

export const useEnvironmentStore = create<EnvironmentState>((set, get) => ({
  // Initial state
  location: null,
  locationError: null,
  locationLoading: false,
  locationPermissionDenied: false,

  weather: null,
  weatherError: null,
  weatherLoading: false,

  lastUpdated: null,
  cacheMinutes: 30,

  /**
   * 获取用户位置
   */
  fetchLocation: async () => {
    const state = get();

    // 如果权限被拒绝，不再尝试
    if (state.locationPermissionDenied) {
      console.log('[EnvironmentStore] Location permission denied, skip fetch');
      return;
    }

    set({ locationLoading: true, locationError: null });

    try {
      const result = await getCurrentLocation({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000, // 允许使用1分钟内的缓存位置
      });

      if (result.success) {
        console.log('[EnvironmentStore] Location fetched:', result.data);
        set({
          location: result.data,
          locationError: null,
          locationLoading: false,
          locationPermissionDenied: false,
        });
      } else {
        console.error('[EnvironmentStore] Location fetch failed:', result.error);

        // 处理权限被拒绝的情况
        if (result.error.code === 'PERMISSION_DENIED') {
          set({
            locationError: result.error,
            locationLoading: false,
            locationPermissionDenied: true,
          });
        } else {
          set({
            locationError: result.error,
            locationLoading: false,
          });
        }
      }
    } catch (error: any) {
      console.error('[EnvironmentStore] Location fetch exception:', error);
      set({
        locationError: {
          code: 'UNKNOWN',
          message: error.message || '获取位置失败',
        },
        locationLoading: false,
      });
    }
  },

  /**
   * 获取天气数据
   */
  fetchWeather: async (forceRefresh = false) => {
    const state = get();

    // 检查缓存
    if (!forceRefresh && state.weather && state.lastUpdated) {
      const now = Date.now();
      const cacheAge = now - state.lastUpdated;

      if (cacheAge < CACHE_DURATION_MS) {
        console.log(`[EnvironmentStore] Using cached weather data (${Math.round(cacheAge / 60000)} min old)`);
        return;
      }
    }

    // 需要位置信息
    if (!state.location) {
      await get().fetchLocation();
      const updatedState = get();
      if (!updatedState.location) {
        console.error('[EnvironmentStore] No location available for weather fetch');
        return;
      }
    }

    const location = get().location!;
    set({ weatherLoading: true, weatherError: null });

    try {
      // 调用后端天气API
      const weatherData = await getCurrentWeather({
        latitude: location.latitude,
        longitude: location.longitude,
      });

      console.log('[EnvironmentStore] Weather fetched:', weatherData);

      set({
        weather: weatherData,
        weatherError: null,
        weatherLoading: false,
        lastUpdated: Date.now(),
      });

      // 异步上报到后端（不阻塞）
      reportEnvironmentData({
        temperature: weatherData.temperature,
        weather: weatherData.weather,
        pressure: weatherData.pressure,
        humidity: weatherData.humidity,
        air_quality: weatherData.air_quality,
        location: weatherData.location, // 只传城市名
      }).catch((error) => {
        console.error('[EnvironmentStore] Report environment data failed:', error);
        // 上报失败不影响用户体验，静默处理
      });
    } catch (error: any) {
      console.error('[EnvironmentStore] Weather fetch failed:', error);
      set({
        weatherError: error.message || '获取天气数据失败',
        weatherLoading: false,
      });
    }
  },

  /**
   * 获取所有环境数据（位置 + 天气）
   */
  fetchAll: async (forceRefresh = false) => {
    console.log('[EnvironmentStore] Fetching all environment data...');

    // 先获取位置
    await get().fetchLocation();

    // 如果位置获取成功，再获取天气
    const state = get();
    if (state.location && !state.locationError) {
      await get().fetchWeather(forceRefresh);
    } else {
      console.warn('[EnvironmentStore] Skip weather fetch due to location error');
    }
  },

  /**
   * 清除所有数据
   */
  clearData: () => {
    set({
      location: null,
      locationError: null,
      locationLoading: false,
      weather: null,
      weatherError: null,
      weatherLoading: false,
      lastUpdated: null,
    });
  },

  /**
   * 设置位置权限被拒绝状态
   */
  setLocationPermissionDenied: (denied: boolean) => {
    set({ locationPermissionDenied: denied });
  },
}));

/**
 * 辅助函数：检查天气数据是否新鲜
 */
export const isWeatherDataFresh = (lastUpdated: number | null, maxAgeMinutes: number = 30): boolean => {
  if (!lastUpdated) return false;
  const ageMs = Date.now() - lastUpdated;
  return ageMs < maxAgeMinutes * 60 * 1000;
};

/**
 * 辅助函数：格式化天气描述
 */
export const formatWeatherDescription = (weather: WeatherData | null): string => {
  if (!weather) return '未知';

  const temp = Math.round(weather.temperature);
  const feelsLike = Math.round(weather.feels_like);

  if (temp === feelsLike) {
    return `${temp}°C, ${weather.weather}`;
  } else {
    return `${temp}°C (体感 ${feelsLike}°C), ${weather.weather}`;
  }
};
