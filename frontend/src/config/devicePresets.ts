/**
 * 设备预设配置
 * 用于开发时在PC浏览器中预览不同设备尺寸的效果
 */

export interface DevicePreset {
  id: string;
  name: string;
  width: number | string;
  height: number | string;
  scale?: number;
  icon: string;
  description?: string;
  category?: 'phone' | 'tablet' | 'desktop' | 'custom';
}

export const DEVICE_PRESETS: Record<string, DevicePreset> = {
  // ========== 桌面模式 ==========
  desktop: {
    id: 'desktop',
    name: '桌面模式',
    width: '100%',
    height: '100%',
    icon: '💻',
    description: '全屏响应式显示',
    category: 'desktop'
  },

  // ========== iPhone 系列 ==========
  // iPhone 15 系列
  iphone15ProMax: {
    id: 'iphone15ProMax',
    name: 'iPhone 15 Pro Max',
    width: 430,
    height: 932,
    scale: 0.9,
    icon: '📱',
    description: '2023最新大屏iPhone',
    category: 'phone'
  },

  iphone15Pro: {
    id: 'iphone15Pro',
    name: 'iPhone 15 Pro',
    width: 393,
    height: 852,
    scale: 1,
    icon: '📱',
    description: '2023最新iPhone',
    category: 'phone'
  },

  // iPhone 14 系列
  iphone14ProMax: {
    id: 'iphone14ProMax',
    name: 'iPhone 14 Pro Max',
    width: 430,
    height: 932,
    scale: 0.9,
    icon: '📱',
    description: '大屏iPhone 14',
    category: 'phone'
  },

  iphone14Pro: {
    id: 'iphone14Pro',
    name: 'iPhone 14 Pro',
    width: 393,
    height: 852,
    scale: 1,
    icon: '📱',
    description: '最常见iPhone尺寸',
    category: 'phone'
  },

  iphone14: {
    id: 'iphone14',
    name: 'iPhone 14',
    width: 390,
    height: 844,
    scale: 1,
    icon: '📱',
    description: 'iPhone 14标准版',
    category: 'phone'
  },

  // iPhone 13 系列
  iphone13ProMax: {
    id: 'iphone13ProMax',
    name: 'iPhone 13 Pro Max',
    width: 428,
    height: 926,
    scale: 0.9,
    icon: '📱',
    description: 'iPhone 13大屏',
    category: 'phone'
  },

  iphone13: {
    id: 'iphone13',
    name: 'iPhone 13',
    width: 390,
    height: 844,
    scale: 1,
    icon: '📱',
    description: '仍然广泛使用',
    category: 'phone'
  },

  iphone13Mini: {
    id: 'iphone13Mini',
    name: 'iPhone 13 Mini',
    width: 375,
    height: 812,
    scale: 1,
    icon: '📱',
    description: '小屏iPhone',
    category: 'phone'
  },

  // iPhone 12 系列
  iphone12ProMax: {
    id: 'iphone12ProMax',
    name: 'iPhone 12 Pro Max',
    width: 428,
    height: 926,
    scale: 0.9,
    icon: '📱',
    description: 'iPhone 12大屏',
    category: 'phone'
  },

  iphone12Mini: {
    id: 'iphone12Mini',
    name: 'iPhone 12 Mini',
    width: 375,
    height: 812,
    scale: 1,
    icon: '📱',
    description: '最小5G iPhone',
    category: 'phone'
  },

  // iPhone X/XS 系列
  iphoneX: {
    id: 'iphoneX',
    name: 'iPhone X/XS',
    width: 375,
    height: 812,
    scale: 1,
    icon: '📱',
    description: '经典全面屏iPhone',
    category: 'phone'
  },

  // iPhone SE
  iphoneSE: {
    id: 'iphoneSE',
    name: 'iPhone SE',
    width: 375,
    height: 667,
    scale: 1,
    icon: '📱',
    description: '紧凑型iPhone',
    category: 'phone'
  },

  // ========== Android 系列 ==========
  // Samsung Galaxy S 系列
  galaxyS23Ultra: {
    id: 'galaxyS23Ultra',
    name: 'Galaxy S23 Ultra',
    width: 412,
    height: 915,
    scale: 0.95,
    icon: '🤖',
    description: '2023三星旗舰',
    category: 'phone'
  },

  galaxyS22: {
    id: 'galaxyS22',
    name: 'Samsung S22',
    width: 360,
    height: 780,
    scale: 1,
    icon: '🤖',
    description: '三星旗舰',
    category: 'phone'
  },

  galaxyS21: {
    id: 'galaxyS21',
    name: 'Samsung S21',
    width: 360,
    height: 800,
    scale: 1,
    icon: '🤖',
    description: '主流Android设备',
    category: 'phone'
  },

  // Samsung A 系列（中端）
  galaxyA: {
    id: 'galaxyA',
    name: 'Samsung A Series',
    width: 360,
    height: 760,
    scale: 1,
    icon: '🤖',
    description: '中端安卓设备',
    category: 'phone'
  },

  // Google Pixel 系列
  pixel7Pro: {
    id: 'pixel7Pro',
    name: 'Google Pixel 7 Pro',
    width: 412,
    height: 892,
    scale: 0.95,
    icon: '🤖',
    description: 'Google最新旗舰',
    category: 'phone'
  },

  pixel7: {
    id: 'pixel7',
    name: 'Google Pixel 7',
    width: 412,
    height: 915,
    scale: 0.95,
    icon: '🤖',
    description: 'Google旗舰',
    category: 'phone'
  },

  pixel6: {
    id: 'pixel6',
    name: 'Google Pixel 6',
    width: 412,
    height: 915,
    scale: 0.95,
    icon: '🤖',
    description: 'Google上代旗舰',
    category: 'phone'
  },

  // 小米系列
  xiaomi13: {
    id: 'xiaomi13',
    name: '小米 13',
    width: 393,
    height: 851,
    scale: 1,
    icon: '🤖',
    description: '国产主流旗舰',
    category: 'phone'
  },

  xiaomiRedmi: {
    id: 'xiaomiRedmi',
    name: 'Redmi Note',
    width: 393,
    height: 873,
    scale: 0.95,
    icon: '🤖',
    description: '红米系列',
    category: 'phone'
  },

  // 华为系列
  huaweiMate: {
    id: 'huaweiMate',
    name: '华为 Mate',
    width: 360,
    height: 780,
    scale: 1,
    icon: '🤖',
    description: '华为旗舰',
    category: 'phone'
  },

  // ========== 平板系列 ==========
  // iPad Pro
  ipadPro129: {
    id: 'ipadPro129',
    name: 'iPad Pro 12.9"',
    width: 1024,
    height: 1366,
    scale: 0.65,
    icon: '📱',
    description: '最大iPad',
    category: 'tablet'
  },

  ipadPro11: {
    id: 'ipadPro11',
    name: 'iPad Pro 11"',
    width: 834,
    height: 1194,
    scale: 0.75,
    icon: '📱',
    description: '专业级平板',
    category: 'tablet'
  },

  // iPad Air
  ipadAir: {
    id: 'ipadAir',
    name: 'iPad Air',
    width: 820,
    height: 1180,
    scale: 0.75,
    icon: '📱',
    description: '中型平板',
    category: 'tablet'
  },

  // iPad 标准版
  ipad: {
    id: 'ipad',
    name: 'iPad',
    width: 768,
    height: 1024,
    scale: 0.8,
    icon: '📱',
    description: '标准平板',
    category: 'tablet'
  },

  // iPad Mini
  ipadMini: {
    id: 'ipadMini',
    name: 'iPad Mini',
    width: 744,
    height: 1133,
    scale: 0.8,
    icon: '📱',
    description: '小平板',
    category: 'tablet'
  },

  // ========== 自定义尺寸 ==========
  customSmall: {
    id: 'customSmall',
    name: '最小尺寸',
    width: 320,
    height: 568,
    scale: 1,
    icon: '📐',
    description: '最小测试尺寸',
    category: 'custom'
  },

  customLarge: {
    id: 'customLarge',
    name: '超大屏幕',
    width: 480,
    height: 1024,
    scale: 0.85,
    icon: '📐',
    description: '超大手机屏幕',
    category: 'custom'
  },
};

// 默认设备（应用首次打开时使用手机模式）
export const DEFAULT_DEVICE = 'iphone14Pro';

// 设备分类
export const DEVICE_CATEGORIES = {
  phone: {
    label: '📱 手机',
    devices: [
      // iPhone 系列
      'iphone15ProMax', 'iphone15Pro',
      'iphone14ProMax', 'iphone14Pro', 'iphone14',
      'iphone13ProMax', 'iphone13', 'iphone13Mini',
      'iphone12ProMax', 'iphone12Mini',
      'iphoneX', 'iphoneSE',

      // Android 系列
      'galaxyS23Ultra', 'galaxyS22', 'galaxyS21', 'galaxyA',
      'pixel7Pro', 'pixel7', 'pixel6',
      'xiaomi13', 'xiaomiRedmi',
      'huaweiMate',
    ]
  },
  tablet: {
    label: '📱 平板',
    devices: [
      'ipadPro129', 'ipadPro11', 'ipadAir', 'ipad', 'ipadMini'
    ]
  },
  desktop: {
    label: '💻 桌面',
    devices: ['desktop']
  },
  custom: {
    label: '⚙️ 自定义',
    devices: ['customSmall', 'customLarge']
  }
};

// 快捷设备列表（常用的前几个）
export const QUICK_DEVICES = [
  'desktop',
  'iphone14Pro',
  'ipad',
];

// 常用的手机设备列表（用于快捷切换）
export const MOBILE_DEVICES = [
  'iphone15ProMax',
  'iphone14Pro',
  'iphone13',
  'iphoneSE',
  'galaxyS23Ultra',
  'pixel7',
  'xiaomi13',
];

// 导出设备ID类型
export type DeviceId = keyof typeof DEVICE_PRESETS;
