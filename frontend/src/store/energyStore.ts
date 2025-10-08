/**
 * Zustand Store for Energy Prediction State Management
 * Handles current energy, predictions, digital twin, and model accuracy
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  EnergyPrediction,
  DigitalTwin,
  EnergyPattern,
  PersonalBaseline,
  ModelAccuracy,
  getCurrentEnergy,
  predictFutureEnergy,
  getDigitalTwin,
  validatePrediction,
  getModelAccuracy,
} from '../api/energy';

interface EnergyState {
  // 状态数据
  currentEnergy: EnergyPrediction | null;
  futurePredictions: EnergyPrediction[];
  digitalTwin: DigitalTwin | null;
  patterns: EnergyPattern[];
  baseline: PersonalBaseline | null;
  modelAccuracy: ModelAccuracy | null;

  // 加载状态
  isLoading: boolean;
  error: string | null;

  // 缓存控制
  lastFetched: number | null;
  cacheDuration: number; // 毫秒，默认5分钟

  // 动作
  fetchCurrentEnergy: () => Promise<void>;
  fetchFuturePredictions: (hours?: number) => Promise<void>;
  fetchDigitalTwin: () => Promise<void>;
  validatePrediction: (predictionId: string, actualEnergy: number) => Promise<void>;
  fetchModelAccuracy: () => Promise<void>;
  clearError: () => void;
  resetStore: () => void;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5分钟

const useEnergyStore = create<EnergyState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      currentEnergy: null,
      futurePredictions: [],
      digitalTwin: null,
      patterns: [],
      baseline: null,
      modelAccuracy: null,
      isLoading: false,
      error: null,
      lastFetched: null,
      cacheDuration: CACHE_DURATION,

      // 获取当前精力状态
      fetchCurrentEnergy: async () => {
        const now = Date.now();
        const { lastFetched, cacheDuration } = get();

        // 缓存检查
        if (lastFetched && now - lastFetched < cacheDuration) {
          return;
        }

        set({ isLoading: true, error: null });

        try {
          const data = await getCurrentEnergy();
          set({
            currentEnergy: data,
            isLoading: false,
            lastFetched: now,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '获取当前精力状态失败',
            isLoading: false,
          });
        }
      },

      // 获取未来精力预测
      fetchFuturePredictions: async (hours = 24) => {
        set({ isLoading: true, error: null });

        try {
          const data = await predictFutureEnergy(hours);
          set({
            futurePredictions: data,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '获取精力预测失败',
            isLoading: false,
          });
        }
      },

      // 获取数字孪生数据
      fetchDigitalTwin: async () => {
        set({ isLoading: true, error: null });

        try {
          const data = await getDigitalTwin();
          set({
            digitalTwin: data,
            currentEnergy: data.current_energy,
            patterns: data.patterns || [],
            baseline: data.baseline,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '获取数字孪生数据失败',
            isLoading: false,
          });
        }
      },

      // 验证预测准确性
      validatePrediction: async (predictionId: string, actualEnergy: number) => {
        set({ isLoading: true, error: null });

        try {
          await validatePrediction(predictionId, actualEnergy);
          set({ isLoading: false });

          // 重新获取模型准确性数据
          await get().fetchModelAccuracy();
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '提交验证数据失败',
            isLoading: false,
          });
        }
      },

      // 获取模型准确性指标
      fetchModelAccuracy: async () => {
        try {
          const data = await getModelAccuracy();
          set({ modelAccuracy: data });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '获取模型准确性数据失败',
          });
        }
      },

      // 清除错误
      clearError: () => set({ error: null }),

      // 重置store
      resetStore: () =>
        set({
          currentEnergy: null,
          futurePredictions: [],
          digitalTwin: null,
          patterns: [],
          baseline: null,
          modelAccuracy: null,
          isLoading: false,
          error: null,
          lastFetched: null,
        }),
    }),
    {
      name: 'energy-store',
    }
  )
);

export default useEnergyStore;
