/**
 * 设备容器组件
 * 根据选择的设备预设，提供对应尺寸的视口容器
 */

import { motion } from 'motion/react';
import { useCurrentDevice, useDevicePreviewStore } from '../store/devicePreviewStore';

interface DeviceFrameProps {
  children: React.ReactNode;
}

export function DeviceFrame({ children }: DeviceFrameProps) {
  const { activeDeviceId, showDeviceFrame, isPreviewEnabled, isLandscape } = useDevicePreviewStore();
  const device = useCurrentDevice();

  // 调试：输出当前状态
  console.log('[DeviceFrame] State:', {
    activeDeviceId,
    isPreviewEnabled,
    showDeviceFrame,
    isLandscape,
    deviceWidth: device.width,
    deviceHeight: device.height
  });

  // 如果预览模式未启用，直接渲染子组件
  if (!isPreviewEnabled) {
    console.warn('[DeviceFrame] Preview mode is DISABLED. Enable it to see device preview.');
    return <>{children}</>;
  }

  // 桌面模式 - 全屏显示
  if (activeDeviceId === 'desktop') {
    console.log('[DeviceFrame] Desktop mode - full screen');
    return <div className="w-full h-screen overflow-hidden">{children}</div>;
  }

  console.log('[DeviceFrame] Mobile preview mode active:', device.name);

  // 计算容器样式
  const containerWidth = typeof device.width === 'number' ? `${device.width}px` : device.width;
  const containerHeight = typeof device.height === 'number' ? `${device.height}px` : device.height;

  // 计算缩放比例（如果设备尺寸超过屏幕，自动缩小）
  const scale = device.scale || 1;

  // iOS安全区域 - 为内容添加CSS变量
  const isIPhone = device.id.toLowerCase().includes('iphone');
  const safeAreaTop = isIPhone && !isLandscape ? '44px' : '0px';
  const safeAreaBottom = isIPhone && !isLandscape ? '34px' : '0px';

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 overflow-auto p-8">
      {/* 设备信息提示（顶部） - 增强版 */}
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
        <div className="bg-black/90 backdrop-blur-sm text-white px-5 py-3 rounded-2xl text-sm font-medium shadow-2xl border border-white/20">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{device.icon}</span>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-bold">{device.name}</span>
                {device.isLandscape && (
                  <span className="bg-blue-500/40 px-2 py-0.5 rounded text-xs">横屏</span>
                )}
              </div>
              <div className="text-gray-300 text-xs flex items-center gap-2">
                <span>
                  {typeof device.width === 'number' ? device.width : '100%'} ×{' '}
                  {typeof device.height === 'number' ? device.height : '100%'}
                </span>
                <span className="text-gray-500">|</span>
                <span className="text-green-400">✓ 预览模式</span>
                {showDeviceFrame && (
                  <>
                    <span className="text-gray-500">|</span>
                    <span className="text-blue-400">边框开启</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 设备容器 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="relative"
        style={{
          width: containerWidth,
          height: containerHeight,
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
        }}
      >
        {/* 设备边框装饰（可选） */}
        {showDeviceFrame && (
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.1)',
              borderRadius: '32px',
            }}
          />
        )}

        {/* 应用内容区域 */}
        <div
          className="relative w-full h-full overflow-y-auto overflow-x-hidden"
          style={{
            borderRadius: showDeviceFrame ? '32px' : '0px',
            // 设置CSS变量供子组件使用
            ['--safe-area-inset-top' as string]: safeAreaTop,
            ['--safe-area-inset-bottom' as string]: safeAreaBottom,
          }}
        >
          {children}
        </div>

        {/* 设备顶部刘海（iPhone样式，可选） */}
        {showDeviceFrame && device.id === 'iphone14Pro' && (
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 z-10">
            <div
              className="bg-black rounded-b-3xl"
              style={{
                width: '120px',
                height: '30px',
              }}
            />
          </div>
        )}

        {/* 设备底部指示器（iPhone样式，可选） */}
        {showDeviceFrame && device.id.startsWith('iphone') && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 z-10">
            <div
              className="bg-black/20 rounded-full"
              style={{
                width: '120px',
                height: '4px',
              }}
            />
          </div>
        )}
      </motion.div>
    </div>
  );
}
