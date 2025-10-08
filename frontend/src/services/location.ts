/**
 * 位置服务
 * 使用Capacitor Geolocation获取用户位置
 * 处理权限请求和错误处理
 */

import { Geolocation, Position, PositionOptions } from '@capacitor/geolocation';
import { isNativePlatform } from '../utils/capacitor';

export interface LocationCoordinates {
  latitude: number;
  longitude: number;
  accuracy: number;
  altitude?: number | null;
  altitudeAccuracy?: number | null;
  heading?: number | null;
  speed?: number | null;
}

export interface LocationError {
  code: string;
  message: string;
}

/**
 * 检查位置权限状态
 */
export const checkLocationPermission = async (): Promise<boolean> => {
  try {
    const permission = await Geolocation.checkPermissions();
    return permission.location === 'granted';
  } catch (error) {
    console.error('[Location] Check permission failed:', error);
    return false;
  }
};

/**
 * 请求位置权限
 */
export const requestLocationPermission = async (): Promise<boolean> => {
  try {
    const permission = await Geolocation.requestPermissions();
    return permission.location === 'granted';
  } catch (error) {
    console.error('[Location] Request permission failed:', error);
    return false;
  }
};

/**
 * 获取当前位置（单次）
 *
 * @param options - 位置选项配置
 * @returns 位置坐标或错误信息
 */
export const getCurrentLocation = async (
  options?: PositionOptions
): Promise<{ success: true; data: LocationCoordinates } | { success: false; error: LocationError }> => {
  // Web端降级处理
  if (!isNativePlatform) {
    if ('geolocation' in navigator) {
      return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              success: true,
              data: {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                altitude: position.coords.altitude,
                altitudeAccuracy: position.coords.altitudeAccuracy,
                heading: position.coords.heading,
                speed: position.coords.speed,
              },
            });
          },
          (error) => {
            resolve({
              success: false,
              error: {
                code: `WEB_${error.code}`,
                message: error.message,
              },
            });
          },
          {
            enableHighAccuracy: options?.enableHighAccuracy ?? true,
            timeout: options?.timeout ?? 10000,
            maximumAge: options?.maximumAge ?? 0,
          }
        );
      });
    } else {
      return {
        success: false,
        error: {
          code: 'WEB_NOT_SUPPORTED',
          message: 'Geolocation is not supported by this browser',
        },
      };
    }
  }

  // 原生平台
  try {
    // 检查权限
    const hasPermission = await checkLocationPermission();
    if (!hasPermission) {
      const granted = await requestLocationPermission();
      if (!granted) {
        return {
          success: false,
          error: {
            code: 'PERMISSION_DENIED',
            message: '位置权限被拒绝，请在设置中开启',
          },
        };
      }
    }

    // 获取位置
    const position: Position = await Geolocation.getCurrentPosition({
      enableHighAccuracy: options?.enableHighAccuracy ?? true,
      timeout: options?.timeout ?? 10000,
      maximumAge: options?.maximumAge ?? 0,
    });

    return {
      success: true,
      data: {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        altitude: position.coords.altitude,
        altitudeAccuracy: position.coords.altitudeAccuracy,
        heading: position.coords.heading,
        speed: position.coords.speed,
      },
    };
  } catch (error: any) {
    console.error('[Location] Get current location failed:', error);

    // 解析错误类型
    let errorCode = 'UNKNOWN';
    let errorMessage = '获取位置失败';

    if (error.message) {
      if (error.message.includes('denied') || error.message.includes('permission')) {
        errorCode = 'PERMISSION_DENIED';
        errorMessage = '位置权限被拒绝';
      } else if (error.message.includes('timeout')) {
        errorCode = 'TIMEOUT';
        errorMessage = '获取位置超时';
      } else if (error.message.includes('unavailable')) {
        errorCode = 'POSITION_UNAVAILABLE';
        errorMessage = '位置信息不可用';
      }
    }

    return {
      success: false,
      error: {
        code: errorCode,
        message: errorMessage,
      },
    };
  }
};

/**
 * 监听位置变化
 *
 * @param callback - 位置更新回调
 * @param errorCallback - 错误回调
 * @param options - 位置选项配置
 * @returns 取消监听的函数
 */
export const watchLocation = async (
  callback: (location: LocationCoordinates) => void,
  errorCallback?: (error: LocationError) => void,
  options?: PositionOptions
): Promise<string | null> => {
  try {
    // 检查权限
    const hasPermission = await checkLocationPermission();
    if (!hasPermission) {
      const granted = await requestLocationPermission();
      if (!granted) {
        errorCallback?.({
          code: 'PERMISSION_DENIED',
          message: '位置权限被拒绝',
        });
        return null;
      }
    }

    // 开始监听
    const watchId = await Geolocation.watchPosition(
      {
        enableHighAccuracy: options?.enableHighAccuracy ?? true,
        timeout: options?.timeout ?? 10000,
        maximumAge: options?.maximumAge ?? 0,
      },
      (position, err) => {
        if (err) {
          errorCallback?.({
            code: 'WATCH_ERROR',
            message: err.message || '位置监听出错',
          });
          return;
        }

        if (position) {
          callback({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            speed: position.coords.speed,
          });
        }
      }
    );

    return watchId;
  } catch (error: any) {
    console.error('[Location] Watch location failed:', error);
    errorCallback?.({
      code: 'WATCH_FAILED',
      message: error.message || '开始位置监听失败',
    });
    return null;
  }
};

/**
 * 停止监听位置变化
 *
 * @param watchId - watchLocation返回的ID
 */
export const clearLocationWatch = async (watchId: string): Promise<void> => {
  try {
    await Geolocation.clearWatch({ id: watchId });
    console.log('[Location] Watch cleared:', watchId);
  } catch (error) {
    console.error('[Location] Clear watch failed:', error);
  }
};

/**
 * 格式化坐标为字符串（用于调试）
 */
export const formatCoordinates = (coords: LocationCoordinates): string => {
  return `${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)} (±${coords.accuracy.toFixed(0)}m)`;
};
