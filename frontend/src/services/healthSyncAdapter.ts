/**
 * 健康数据同步适配器
 * 自动检测并使用真实插件或模拟服务
 */

import { Capacitor } from '@capacitor/core';
import type { HealthDataSyncOptions, SyncResult } from './healthSync';

// 动态导入
let useRealPlugin = false;

// 检查是否可以使用真实插件
async function checkPluginAvailability(): Promise<boolean> {
  try {
    // 只在原生平台尝试加载
    if (Capacitor.getPlatform() === 'web') {
      return false;
    }

    // 尝试导入 Health 插件
    const { Health } = await import('capacitor-health');
    if (Health) {
      console.log('✅ 检测到 capacitor-health 插件');
      return true;
    }
  } catch (error) {
    console.log('⚠️ capacitor-health 插件不可用，使用模拟数据');
    console.log('错误详情:', error);
  }
  return false;
}

// 初始化健康同步
export async function initHealthSync(): Promise<boolean> {
  useRealPlugin = await checkPluginAvailability();

  if (useRealPlugin) {
    const { initHealthSync: initReal } = await import('./healthSync');
    return initReal();
  } else {
    const { initHealthSyncMock } = await import('./healthSyncMock');
    return initHealthSyncMock();
  }
}

// 检查权限
export async function checkHealthPermissions(): Promise<boolean> {
  if (useRealPlugin) {
    const { checkHealthPermissions: checkReal } = await import('./healthSync');
    return checkReal();
  } else {
    const { checkHealthPermissionsMock } = await import('./healthSyncMock');
    return checkHealthPermissionsMock();
  }
}

// 同步健康数据
export async function syncHealthDataNow(
  options: HealthDataSyncOptions = {}
): Promise<SyncResult> {
  // 重新检查插件可用性
  useRealPlugin = await checkPluginAvailability();

  if (useRealPlugin) {
    const { syncHealthDataNow: syncReal } = await import('./healthSync');
    return syncReal(options);
  } else {
    const { syncHealthDataNowMock } = await import('./healthSyncMock');
    return syncHealthDataNowMock(options);
  }
}

// 导出类型
export type { HealthDataSyncOptions, SyncResult } from './healthSync';
