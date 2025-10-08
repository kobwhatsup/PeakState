/**
 * 健康数据同步服务 - 模拟版本
 * 用于在无法使用 capacitor-health 插件时进行测试
 */

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

class HealthSyncServiceMock {
  private isInitialized = false;

  async initialize(): Promise<boolean> {
    console.log('📱 使用模拟健康数据服务（CocoaPods未安装）');

    // 模拟初始化延迟
    await new Promise(resolve => setTimeout(resolve, 500));

    this.isInitialized = true;
    return true;
  }

  async syncSleepData(startDate: Date, endDate: Date): Promise<any[]> {
    console.log('😴 模拟同步睡眠数据:', { startDate, endDate });

    // 生成模拟睡眠数据
    const mockData = [];
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    for (let i = 0; i < Math.min(days, 7); i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);

      mockData.push({
        value: 6.5 + Math.random() * 2, // 6.5-8.5 小时
        date: date.toISOString().split('T')[0],
        metadata: {
          source: 'mock',
          quality: 'good'
        }
      });
    }

    return mockData;
  }

  async syncStepsData(startDate: Date, endDate: Date): Promise<any[]> {
    console.log('🚶 模拟同步步数数据:', { startDate, endDate });

    const mockData = [];
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    for (let i = 0; i < Math.min(days, 7); i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);

      mockData.push({
        value: 5000 + Math.random() * 5000, // 5000-10000 步
        date: date.toISOString().split('T')[0],
        metadata: {
          source: 'mock'
        }
      });
    }

    return mockData;
  }

  async syncHeartRateData(startDate: Date, endDate: Date): Promise<any[]> {
    console.log('❤️ 模拟同步心率数据:', { startDate, endDate });

    const mockData = [];
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    for (let i = 0; i < Math.min(days, 7); i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);

      mockData.push({
        value: 60 + Math.random() * 40, // 60-100 bpm
        date: date.toISOString().split('T')[0],
        metadata: {
          source: 'mock'
        }
      });
    }

    return mockData;
  }

  async syncActivityData(startDate: Date, endDate: Date): Promise<any[]> {
    console.log('🏃 模拟同步活动数据:', { startDate, endDate });

    const mockData = [];
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    for (let i = 0; i < Math.min(days, 7); i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);

      mockData.push({
        value: {
          calories: 200 + Math.random() * 300, // 200-500 卡路里
          distance: 2 + Math.random() * 3 // 2-5 公里
        },
        date: date.toISOString().split('T')[0],
        metadata: {
          source: 'mock'
        }
      });
    }

    return mockData;
  }

  async syncAll(options: HealthDataSyncOptions = {}): Promise<SyncResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const endDate = options.endDate || new Date();
    const startDate = options.startDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const types = options.types || ['sleep', 'steps', 'heart_rate', 'activity'];

    console.log('🔄 开始同步健康数据（模拟）:', { startDate, endDate, types });

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

    try {
      // 模拟同步延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (types.includes('sleep')) {
        const data = await this.syncSleepData(startDate, endDate);
        result.synced.sleep = data.length;
      }

      if (types.includes('steps')) {
        const data = await this.syncStepsData(startDate, endDate);
        result.synced.steps = data.length;
      }

      if (types.includes('heart_rate')) {
        const data = await this.syncHeartRateData(startDate, endDate);
        result.synced.heartRate = data.length;
      }

      if (types.includes('activity')) {
        const data = await this.syncActivityData(startDate, endDate);
        result.synced.activity = data.length;
      }

      console.log('✅ 模拟同步完成:', result);
    } catch (error) {
      console.error('❌ 模拟同步失败:', error);
      result.success = false;
      result.errors.push(error instanceof Error ? error.message : '未知错误');
    }

    return result;
  }
}

export const healthSyncServiceMock = new HealthSyncServiceMock();

// 导出辅助函数
export async function initHealthSyncMock(): Promise<boolean> {
  return healthSyncServiceMock.initialize();
}

export async function checkHealthPermissionsMock(): Promise<boolean> {
  console.log('✅ 模拟权限检查通过');
  return true;
}

export async function syncHealthDataNowMock(
  options: HealthDataSyncOptions = {}
): Promise<SyncResult> {
  return healthSyncServiceMock.syncAll(options);
}
