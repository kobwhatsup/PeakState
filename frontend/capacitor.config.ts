import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.peakstate.app',
  appName: 'PeakState',
  webDir: 'dist',
  bundledWebRuntime: false,

  server: {
    // 开发时使用本地服务器（需要时取消注释）
    // url: 'http://localhost:3000',
    // cleartext: true,
  },

  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#2B69B6',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#2B69B6',
      overlaysWebView: false,
    },
    Health: {
      // iOS HealthKit配置
      ios: {
        // 启用后台健康数据同步
        backgroundDeliveryEnabled: true,
      },
      // Android Health Connect配置
      android: {
        // Health Connect包名
        packageName: 'com.google.android.apps.healthdata',
      },
    },
  },

  ios: {
    contentInset: 'always',
  },

  android: {
    buildOptions: {
      keystorePath: undefined,
      keystoreAlias: undefined,
    },
  },
};

export default config;
