import { Capacitor } from '@capacitor/core';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';

// 检测是否运行在原生平台
export const isNativePlatform = Capacitor.isNativePlatform();

// 获取当前平台 ('ios', 'android', 或 'web')
export const platform = Capacitor.getPlatform();

/**
 * 初始化 Capacitor 原生功能
 * 在 App 启动时调用
 */
export const initCapacitor = async () => {
  if (!isNativePlatform) {
    console.log('[Capacitor] Running on web platform');
    return;
  }

  console.log(`[Capacitor] Initializing on ${platform} platform`);

  // 配置状态栏
  try {
    await StatusBar.setStyle({ style: Style.Light });
    if (platform === 'android') {
      await StatusBar.setBackgroundColor({ color: '#2B69B6' });
    }
    console.log('[Capacitor] StatusBar configured');
  } catch (error) {
    console.error('[Capacitor] StatusBar setup failed:', error);
  }

  // 隐藏启动屏幕
  try {
    await SplashScreen.hide();
    console.log('[Capacitor] SplashScreen hidden');
  } catch (error) {
    console.error('[Capacitor] SplashScreen hide failed:', error);
  }
};

/**
 * 在需要时显示状态栏
 */
export const showStatusBar = async () => {
  if (!isNativePlatform) return;
  try {
    await StatusBar.show();
  } catch (error) {
    console.error('[Capacitor] Show StatusBar failed:', error);
  }
};

/**
 * 在需要时隐藏状态栏
 */
export const hideStatusBar = async () => {
  if (!isNativePlatform) return;
  try {
    await StatusBar.hide();
  } catch (error) {
    console.error('[Capacitor] Hide StatusBar failed:', error);
  }
};
