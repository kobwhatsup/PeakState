/**
 * 设备预览切换按钮
 * 浮动在右下角的设备模式切换器
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Monitor, Smartphone, Tablet, RotateCw, X } from 'lucide-react';
import { useDevicePreviewStore } from '../store/devicePreviewStore';
import { DEVICE_PRESETS, MOBILE_DEVICES } from '../config/devicePresets';

export function DevicePreviewToggle() {
  const [isOpen, setIsOpen] = useState(false);
  const { activeDeviceId, setDevice, rotateDevice, isLandscape, isPreviewEnabled, togglePreview, reset } = useDevicePreviewStore();

  // 快捷键支持
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Cmd/Ctrl + D: 切换设备模式（桌面 ↔ 手机）
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        if (activeDeviceId === 'desktop') {
          setDevice('iphone14Pro');
        } else {
          setDevice('desktop');
        }
      }

      // Cmd/Ctrl + R: 旋转设备
      if ((e.metaKey || e.ctrlKey) && e.key === 'r') {
        e.preventDefault();
        rotateDevice();
      }

      // Cmd/Ctrl + T: 打开/关闭切换面板
      if ((e.metaKey || e.ctrlKey) && e.key === 't') {
        e.preventDefault();
        setIsOpen(!isOpen);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [activeDeviceId, setDevice, rotateDevice, isOpen]);

  // 快捷设备按钮列表
  const quickDevices = [
    { id: 'desktop', icon: Monitor, label: '桌面', shortcut: '⌘D' },
    { id: 'iphone14Pro', icon: Smartphone, label: '手机', shortcut: '⌘D' },
    { id: 'ipad', icon: Tablet, label: '平板', shortcut: '' },
  ];

  return (
    <>
      {/* 预览模式禁用警告 */}
      {!isPreviewEnabled && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50"
        >
          <div className="bg-red-500 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-bold">设备预览模式已禁用</p>
              <p className="text-xs text-red-100">点击右下角按钮重新启用</p>
            </div>
            <button
              onClick={togglePreview}
              className="bg-white text-red-500 px-4 py-2 rounded-lg font-bold hover:bg-red-50 transition-colors"
            >
              启用
            </button>
          </div>
        </motion.div>
      )}

      {/* 主切换按钮 */}
      <motion.div
        className="fixed bottom-6 right-6 z-50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`backdrop-blur-sm hover:scale-110 text-white p-4 rounded-full shadow-2xl transition-all duration-300 ${
            isPreviewEnabled
              ? 'bg-black/80 hover:bg-black'
              : 'bg-red-500/80 hover:bg-red-500 animate-pulse'
          }`}
          title="设备预览切换器 (⌘T)"
        >
          {activeDeviceId === 'desktop' ? (
            <Monitor className="w-6 h-6" />
          ) : (
            <Smartphone className="w-6 h-6" />
          )}
        </button>
      </motion.div>

      {/* 展开的设备选择面板 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-24 right-6 z-50 bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-gray-200 p-4 min-w-[280px]"
          >
            {/* 标题栏 */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900">设备预览</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* 快捷设备按钮组 */}
            <div className="space-y-2 mb-4">
              {quickDevices.map((device) => {
                const Icon = device.icon;
                const isActive = activeDeviceId === device.id;

                return (
                  <button
                    key={device.id}
                    onClick={() => {
                      setDevice(device.id as any);
                      setIsOpen(false);
                    }}
                    className={`
                      w-full flex items-center justify-between px-4 py-3 rounded-xl
                      transition-all duration-200
                      ${
                        isActive
                          ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                          : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{device.label}</span>
                    </div>
                    {device.shortcut && (
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          isActive ? 'bg-blue-600' : 'bg-gray-200 text-gray-600'
                        }`}
                      >
                        {device.shortcut}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* 其他手机设备选项 */}
            <div className="border-t border-gray-200 pt-3">
              <p className="text-xs text-gray-500 mb-2 px-1">其他设备</p>
              <div className="grid grid-cols-2 gap-2">
                {MOBILE_DEVICES.filter((id) => id !== 'iphone14Pro').map((deviceId) => {
                  const device = DEVICE_PRESETS[deviceId];
                  const isActive = activeDeviceId === deviceId;

                  return (
                    <button
                      key={deviceId}
                      onClick={() => {
                        setDevice(deviceId as any);
                        setIsOpen(false);
                      }}
                      className={`
                        px-3 py-2 rounded-lg text-xs font-medium transition-all
                        ${
                          isActive
                            ? 'bg-blue-100 text-blue-700 border border-blue-300'
                            : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-transparent'
                        }
                      `}
                    >
                      {device.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 旋转按钮（仅手机/平板模式显示） */}
            {activeDeviceId !== 'desktop' && (
              <div className="border-t border-gray-200 pt-3 mt-3">
                <button
                  onClick={() => {
                    rotateDevice();
                  }}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-gray-50 text-gray-700 hover:bg-gray-100 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <RotateCw className="w-5 h-5" />
                    <span className="font-medium">旋转设备</span>
                  </div>
                  <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                    ⌘R
                  </span>
                </button>
                {isLandscape && (
                  <p className="text-xs text-gray-500 mt-2 text-center">当前：横屏模式</p>
                )}
              </div>
            )}

            {/* 工具按钮 */}
            <div className="mt-4 pt-3 border-t border-gray-200 space-y-2">
              <button
                onClick={() => {
                  reset();
                  setIsOpen(false);
                }}
                className="w-full px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-all text-sm font-medium"
              >
                🔄 重置为默认设备
              </button>

              <button
                onClick={togglePreview}
                className={`w-full px-4 py-2 rounded-lg transition-all text-sm font-medium ${
                  isPreviewEnabled
                    ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border border-yellow-200'
                    : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
                }`}
              >
                {isPreviewEnabled ? '❌ 禁用预览模式' : '✅ 启用预览模式'}
              </button>
            </div>

            {/* 提示信息 */}
            <div className="mt-4 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-400 text-center">
                💡 使用 <kbd className="px-1 py-0.5 bg-gray-100 rounded text-gray-600">⌘D</kbd>{' '}
                快速切换桌面/手机模式
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
