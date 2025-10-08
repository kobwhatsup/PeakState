/**
 * 健康数据同步测试页面
 * 用于测试 iPhone 健康数据同步功能
 */

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import HealthDataPermission from '../components/HealthDataPermission';

export const HealthSyncTest: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4">
      {/* 标题栏 */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => window.history.back()}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回
        </Button>

        <h1 className="text-2xl font-bold text-gray-900">
          健康数据同步测试
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          测试 Apple Health 数据同步功能
        </p>
      </div>

      {/* 健康数据权限组件 */}
      <HealthDataPermission
        onPermissionGranted={() => {
          console.log('✅ 健康数据权限已授予');
        }}
        onPermissionDenied={() => {
          console.log('❌ 健康数据权限被拒绝');
        }}
        autoSync={true}
      />

      {/* 测试说明 */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <h2 className="font-semibold text-gray-900 mb-3">测试步骤：</h2>
        <ol className="space-y-2 text-sm text-gray-700">
          <li className="flex gap-2">
            <span className="font-semibold">1.</span>
            <span>点击"连接Apple Health"按钮</span>
          </li>
          <li className="flex gap-2">
            <span className="font-semibold">2.</span>
            <span>在弹出的权限窗口中，授予所有健康数据读取权限</span>
          </li>
          <li className="flex gap-2">
            <span className="font-semibold">3.</span>
            <span>授权后会自动同步最近7天的健康数据</span>
          </li>
          <li className="flex gap-2">
            <span className="font-semibold">4.</span>
            <span>查看同步结果，确认成功同步的记录数量</span>
          </li>
          <li className="flex gap-2">
            <span className="font-semibold">5.</span>
            <span>可以点击"立即同步健康数据"按钮手动触发同步</span>
          </li>
        </ol>
      </div>

      {/* 调试信息 */}
      <div className="mt-6 bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-xs">
        <p className="mb-2">📱 设备信息：{navigator.userAgent}</p>
        <p>🏥 健康插件：capacitor-health v7.0.0</p>
      </div>
    </div>
  );
};

export default HealthSyncTest;
