/**
 * 健康数据权限请求组件
 * 引导用户授予健康数据访问权限
 */

import React, { useState, useEffect } from 'react';
import { Activity, Heart, Moon, TrendingUp, Check, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import {
  healthSyncService,
  initHealthSync,
  checkHealthPermissions,
  syncHealthDataNow,
} from '../services/healthSync';
import { Capacitor } from '@capacitor/core';

interface HealthDataPermissionProps {
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  autoSync?: boolean; // 是否在授权后自动同步
}

export const HealthDataPermission: React.FC<HealthDataPermissionProps> = ({
  onPermissionGranted,
  onPermissionDenied,
  autoSync = true,
}) => {
  const [permissionStatus, setPermissionStatus] = useState<'unknown' | 'granted' | 'denied'>('unknown');
  const [isRequesting, setIsRequesting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const platform = Capacitor.getPlatform();

  // 检查权限状态
  useEffect(() => {
    checkPermissionStatus();
  }, []);

  const checkPermissionStatus = async () => {
    try {
      const hasPermission = await checkHealthPermissions();
      setPermissionStatus(hasPermission ? 'granted' : 'unknown');
    } catch (err) {
      console.error('检查权限状态失败:', err);
    }
  };

  // 请求健康数据权限
  const requestPermission = async () => {
    setIsRequesting(true);
    setError(null);

    try {
      const success = await initHealthSync();

      if (success) {
        setPermissionStatus('granted');
        onPermissionGranted?.();

        // 如果启用自动同步，立即同步一次
        if (autoSync) {
          await syncHealthData();
        }
      } else {
        setPermissionStatus('denied');
        setError('无法获取健康数据权限，请在系统设置中允许访问。');
        onPermissionDenied?.();
      }
    } catch (err) {
      console.error('请求权限失败:', err);
      setError('请求权限时出错，请重试。');
      setPermissionStatus('denied');
      onPermissionDenied?.();
    } finally {
      setIsRequesting(false);
    }
  };

  // 同步健康数据
  const syncHealthData = async () => {
    setIsSyncing(true);
    setSyncResult(null);
    setError(null);

    try {
      const result = await syncHealthDataNow({
        types: ['sleep', 'steps', 'heart_rate', 'activity'],
      });

      if (result.success) {
        const totalSynced =
          result.synced.sleep +
          result.synced.steps +
          result.synced.heartRate +
          result.synced.activity;

        setSyncResult(
          `成功同步 ${totalSynced} 条健康数据记录\n` +
            `睡眠: ${result.synced.sleep} | 步数: ${result.synced.steps} | ` +
            `心率: ${result.synced.heartRate} | 活动: ${result.synced.activity}`
        );
      } else {
        setError(`同步失败: ${result.errors.join(', ')}`);
      }
    } catch (err) {
      console.error('同步健康数据失败:', err);
      setError('同步健康数据时出错，请重试。');
    } finally {
      setIsSyncing(false);
    }
  };

  // Web平台不支持健康数据同步
  if (platform === 'web') {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          健康数据同步仅在iOS和Android移动设备上可用。
        </AlertDescription>
      </Alert>
    );
  }

  // 已授权状态
  if (permissionStatus === 'granted') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Check className="h-5 w-5 text-green-500" />
            健康数据已连接
          </CardTitle>
          <CardDescription>
            {platform === 'ios' ? 'Apple Health' : 'Google Fit'} 数据同步已启用
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {syncResult && (
            <Alert className="bg-green-50 border-green-200">
              <Check className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800 whitespace-pre-line">
                {syncResult}
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button
            onClick={syncHealthData}
            disabled={isSyncing}
            className="w-full"
          >
            {isSyncing ? '同步中...' : '立即同步健康数据'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // 请求权限界面
  return (
    <Card>
      <CardHeader>
        <CardTitle>连接健康数据</CardTitle>
        <CardDescription>
          授权PeakState访问您的健康数据，以提供个性化的精力管理建议
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 数据类型说明 */}
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <Moon className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <p className="font-medium">睡眠数据</p>
              <p className="text-sm text-muted-foreground">
                分析您的睡眠质量，优化作息建议
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Activity className="h-5 w-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">运动数据</p>
              <p className="text-sm text-muted-foreground">
                追踪步数、卡路里和运动时长
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Heart className="h-5 w-5 text-red-500 mt-0.5" />
            <div>
              <p className="font-medium">心率数据</p>
              <p className="text-sm text-muted-foreground">
                监测心率变化，评估压力水平
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <TrendingUp className="h-5 w-5 text-purple-500 mt-0.5" />
            <div>
              <p className="font-medium">活动数据</p>
              <p className="text-sm text-muted-foreground">
                记录日常活动，计算精力消耗
              </p>
            </div>
          </div>
        </div>

        {/* 隐私说明 */}
        <div className="bg-muted/50 rounded-lg p-4 text-sm">
          <p className="font-medium mb-2">🔒 您的隐私受保护</p>
          <ul className="space-y-1 text-muted-foreground">
            <li>• 数据仅用于生成个性化建议</li>
            <li>• 不会与第三方共享您的健康数据</li>
            <li>• 您可以随时撤销访问权限</li>
          </ul>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Button
          onClick={requestPermission}
          disabled={isRequesting}
          className="w-full"
          size="lg"
        >
          {isRequesting ? '请求中...' : `连接${platform === 'ios' ? 'Apple Health' : 'Google Fit'}`}
        </Button>
      </CardContent>
    </Card>
  );
};

export default HealthDataPermission;
