/**
 * 健康数据同步服务
 * 集成 Apple HealthKit 和 Android Health Connect
 */

import { Health } from 'capacitor-health';
import { Capacitor } from '@capacitor/core';
import { syncHealthData as apiSyncHealthData } from '../api';

export interface HealthDataSyncOptions {
  startDate?: Date;
  endDate?: Date;
  types?: ('sleep' | 'steps' | 'heart_rate' | 'activity')[];
}

export interface SyncResult {
  success: boolean;
  synced: {
    sleep: number;
    steps: number;
    heartRate: number;
    activity: number;
  };
  errors: string[];
}

/**
 * 健康数据同步管理器
 */
class HealthSyncService {
  private isInitialized = false;
  private platform: 'ios' | 'android' | 'web' = 'web';

  constructor() {
    this.platform = Capacitor.getPlatform() as 'ios' | 'android' | 'web';
  }

  /**
   * 初始化健康数据权限
   */
  async initialize(): Promise<boolean> {
    if (this.platform === 'web') {
      console.log('健康数据同步在Web平台不可用');
      return false;
    }

    try {
      // 请求健康数据权限 - 使用正确的 API
      const permissions = await Health.requestHealthPermissions({
        permissions: [
          'READ_STEPS',
          'READ_DISTANCE',
          'READ_ACTIVE_CALORIES',
          'READ_HEART_RATE',
          'READ_WORKOUTS',
        ],
      });

      console.log('健康数据权限:', permissions);
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('初始化健康数据权限失败:', error);
      return false;
    }
  }

  /**
   * 检查健康数据权限状态
   */
  async checkPermissions(): Promise<boolean> {
    if (this.platform === 'web') {
      return false;
    }

    try {
      const status = await Health.isAvailable();
      return status.available;
    } catch (error) {
      console.error('检查健康数据权限失败:', error);
      return false;
    }
  }

  /**
   * 同步睡眠数据
   */
  async syncSleepData(startDate: Date, endDate: Date): Promise<any[]> {
    if (!this.isInitialized) {
      throw new Error('健康数据服务未初始化');
    }

    try {
      // 注意：capacitor-health 不直接支持睡眠数据的聚合查询
      // 我们使用 queryWorkouts 来获取睡眠数据
      const response = await Health.queryWorkouts({
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        includeHeartRate: false,
        includeRoute: false,
        includeSteps: false,
      });

      console.log('运动和睡眠数据:', response);

      // 过滤出睡眠数据并转换为标准格式
      const sleepWorkouts = response.workouts.filter((w: any) =>
        w.workoutType?.toLowerCase().includes('sleep') || w.workoutActivityType === 'SLEEP'
      );

      const records = sleepWorkouts.map((item: any) => ({
        type: 'sleep',
        date: item.startDate?.split('T')[0] || new Date().toISOString().split('T')[0],
        value: item.duration ? item.duration / 3600 : 0, // 转换为小时
        metadata: {
          startDate: item.startDate,
          endDate: item.endDate,
          source: this.platform === 'ios' ? 'apple_health' : 'google_fit',
        },
      }));

      return records;
    } catch (error) {
      console.error('同步睡眠数据失败:', error);
      throw error;
    }
  }

  /**
   * 同步步数数据
   */
  async syncStepsData(startDate: Date, endDate: Date): Promise<any[]> {
    if (!this.isInitialized) {
      throw new Error('健康数据服务未初始化');
    }

    try {
      const response = await Health.queryAggregated({
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        dataType: 'steps',
        bucket: 'day', // 按天聚合
      });

      console.log('步数数据:', response);

      const records = response.aggregatedData.map((item: any) => ({
        type: 'steps',
        date: item.startDate?.split('T')[0] || new Date().toISOString().split('T')[0],
        value: item.value || 0,
        metadata: {
          source: this.platform === 'ios' ? 'apple_health' : 'google_fit',
        },
      }));

      return records;
    } catch (error) {
      console.error('同步步数数据失败:', error);
      throw error;
    }
  }

  /**
   * 同步心率数据
   */
  async syncHeartRateData(startDate: Date, endDate: Date): Promise<any[]> {
    if (!this.isInitialized) {
      throw new Error('健康数据服务未初始化');
    }

    try {
      // 从 workouts 中获取心率数据
      const response = await Health.queryWorkouts({
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        includeHeartRate: true, // 包含心率数据
        includeRoute: false,
        includeSteps: false,
      });

      console.log('运动心率数据:', response);

      // 提取心率数据
      const records: any[] = [];
      response.workouts.forEach((workout: any) => {
        if (workout.heartRateAvg) {
          records.push({
            type: 'heart_rate',
            date: workout.startDate?.split('T')[0] || new Date().toISOString().split('T')[0],
            value: workout.heartRateAvg,
            metadata: {
              timestamp: workout.startDate,
              source: this.platform === 'ios' ? 'apple_health' : 'google_fit',
            },
          });
        }
      });

      return records;
    } catch (error) {
      console.error('同步心率数据失败:', error);
      throw error;
    }
  }

  /**
   * 同步活动数据（卡路里、距离等）
   */
  async syncActivityData(startDate: Date, endDate: Date): Promise<any[]> {
    if (!this.isInitialized) {
      throw new Error('健康数据服务未初始化');
    }

    try {
      // 获取卡路里数据
      const response = await Health.queryAggregated({
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        dataType: 'active-calories',
        bucket: 'day',
      });

      console.log('活动数据（卡路里）:', response);

      // 转换为活动记录
      const records = response.aggregatedData.map((item: any) => ({
        type: 'activity',
        date: item.startDate?.split('T')[0] || new Date().toISOString().split('T')[0],
        value: item.value || 0, // 卡路里值
        metadata: {
          source: this.platform === 'ios' ? 'apple_health' : 'google_fit',
        },
      }));

      return records;
    } catch (error) {
      console.error('同步活动数据失败:', error);
      throw error;
    }
  }

  /**
   * 执行完整的健康数据同步
   */
  async syncAll(options: HealthDataSyncOptions = {}): Promise<SyncResult> {
    const {
      startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 默认最近7天
      endDate = new Date(),
      types = ['sleep', 'steps', 'heart_rate', 'activity'],
    } = options;

    const result: SyncResult = {
      success: true,
      synced: {
        sleep: 0,
        steps: 0,
        heartRate: 0,
        activity: 0,
      },
      errors: [],
    };

    // 确保已初始化
    if (!this.isInitialized) {
      const initialized = await this.initialize();
      if (!initialized) {
        result.success = false;
        result.errors.push('无法初始化健康数据权限');
        return result;
      }
    }

    try {
      // 同步各类数据
      const allRecords: any[] = [];

      if (types.includes('sleep')) {
        try {
          const sleepRecords = await this.syncSleepData(startDate, endDate);
          allRecords.push(...sleepRecords);
          result.synced.sleep = sleepRecords.length;
        } catch (error) {
          result.errors.push(`睡眠数据同步失败: ${error}`);
        }
      }

      if (types.includes('steps')) {
        try {
          const stepsRecords = await this.syncStepsData(startDate, endDate);
          allRecords.push(...stepsRecords);
          result.synced.steps = stepsRecords.length;
        } catch (error) {
          result.errors.push(`步数数据同步失败: ${error}`);
        }
      }

      if (types.includes('heart_rate')) {
        try {
          const heartRateRecords = await this.syncHeartRateData(startDate, endDate);
          allRecords.push(...heartRateRecords);
          result.synced.heartRate = heartRateRecords.length;
        } catch (error) {
          result.errors.push(`心率数据同步失败: ${error}`);
        }
      }

      if (types.includes('activity')) {
        try {
          const activityRecords = await this.syncActivityData(startDate, endDate);
          allRecords.push(...activityRecords);
          result.synced.activity = activityRecords.length;
        } catch (error) {
          result.errors.push(`活动数据同步失败: ${error}`);
        }
      }

      // 上传到后端
      if (allRecords.length > 0) {
        try {
          await apiSyncHealthData({
            data_source: this.platform === 'ios' ? 'apple_health' : 'google_fit',
            data_type: 'batch', // 批量上传
            records: allRecords,
          });
          console.log(`成功上传 ${allRecords.length} 条健康数据记录`);
        } catch (error) {
          result.success = false;
          result.errors.push(`上传到服务器失败: ${error}`);
        }
      }

      return result;
    } catch (error) {
      result.success = false;
      result.errors.push(`同步过程出错: ${error}`);
      return result;
    }
  }

  /**
   * 设置自动同步（每天执行一次）
   */
  async setupAutoSync(): Promise<void> {
    // TODO: 使用后台任务插件实现自动同步
    // 这需要配合后台任务调度器
    console.log('自动同步功能待实现');
  }
}

// 导出单例
export const healthSyncService = new HealthSyncService();

// 便捷方法
export async function initHealthSync(): Promise<boolean> {
  return healthSyncService.initialize();
}

export async function syncHealthDataNow(
  options?: HealthDataSyncOptions
): Promise<SyncResult> {
  return healthSyncService.syncAll(options);
}

export async function checkHealthPermissions(): Promise<boolean> {
  return healthSyncService.checkPermissions();
}
