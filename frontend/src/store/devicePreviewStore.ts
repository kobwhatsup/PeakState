/**
 * 设备预览状态管理
 * 用于在开发时切换不同设备尺寸的预览模式
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { DEVICE_PRESETS, DEFAULT_DEVICE, type DeviceId } from '../config/devicePresets';

interface DevicePreviewState {
  // 当前激活的设备ID
  activeDeviceId: DeviceId;

  // 是否显示设备边框装饰
  showDeviceFrame: boolean;

  // 是否启用预览模式（开发模式下默认启用）
  isPreviewEnabled: boolean;

  // 当前是否为横屏模式
  isLandscape: boolean;

  // 动作方法
  setDevice: (deviceId: DeviceId) => void;
  toggleDeviceFrame: () => void;
  togglePreview: () => void;
  rotateDevice: () => void;
  reset: () => void;
}

export const useDevicePreviewStore = create<DevicePreviewState>()(
  persist(
    (set, get) => ({
      // 初始状态
      activeDeviceId: DEFAULT_DEVICE,
      showDeviceFrame: true,
      isPreviewEnabled: import.meta.env.DEV, // 仅在开发环境启用
      isLandscape: false,

      // 切换设备
      setDevice: (deviceId: DeviceId) => {
        console.log('[DevicePreview] Switching to device:', deviceId);
        set({
          activeDeviceId: deviceId,
          // 桌面模式下隐藏设备边框
          showDeviceFrame: deviceId !== 'desktop'
        });
      },

      // 切换设备边框显示
      toggleDeviceFrame: () => {
        const { showDeviceFrame } = get();
        console.log('[DevicePreview] Toggle device frame:', !showDeviceFrame);
        set({ showDeviceFrame: !showDeviceFrame });
      },

      // 切换预览模式启用状态
      togglePreview: () => {
        const { isPreviewEnabled } = get();
        console.log('[DevicePreview] Toggle preview:', !isPreviewEnabled);
        set({ isPreviewEnabled: !isPreviewEnabled });
      },

      // 旋转设备（横屏/竖屏切换）
      rotateDevice: () => {
        const { isLandscape, activeDeviceId } = get();

        // 桌面模式不支持旋转
        if (activeDeviceId === 'desktop') {
          console.log('[DevicePreview] Desktop mode does not support rotation');
          return;
        }

        console.log('[DevicePreview] Rotate device:', isLandscape ? 'portrait' : 'landscape');
        set({ isLandscape: !isLandscape });
      },

      // 重置到默认状态
      reset: () => {
        console.log('[DevicePreview] Reset to default');
        set({
          activeDeviceId: DEFAULT_DEVICE,
          showDeviceFrame: true,
          isLandscape: false,
        });
      },
    }),
    {
      name: 'peakstate-device-preview', // localStorage key
      partialize: (state) => ({
        // 只持久化用户偏好设置
        activeDeviceId: state.activeDeviceId,
        showDeviceFrame: state.showDeviceFrame,
        isPreviewEnabled: state.isPreviewEnabled,
      }),
    }
  )
);

// 导出便捷的hook用于获取当前设备信息
export const useCurrentDevice = () => {
  const { activeDeviceId, isLandscape } = useDevicePreviewStore();
  const device = DEVICE_PRESETS[activeDeviceId];

  // 如果是横屏，交换宽高
  if (isLandscape && device.id !== 'desktop') {
    return {
      ...device,
      width: device.height,
      height: device.width,
      isLandscape: true,
    };
  }

  return {
    ...device,
    isLandscape: false,
  };
};

// 快捷键支持（在组件中使用）
export const DEVICE_PREVIEW_SHORTCUTS = {
  TOGGLE_DEVICE: 'mod+d', // Cmd/Ctrl + D
  ROTATE: 'mod+r', // Cmd/Ctrl + R
  TOGGLE_FRAME: 'mod+f', // Cmd/Ctrl + F
  RESET: 'Escape', // Esc
};
