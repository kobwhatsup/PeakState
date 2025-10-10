# PeakState - AI精力管理教练

## 项目简介

巅峰态(PeakState)是一款基于AI技术的个性化精力管理iOS应用。通过7x24小时在线的AI教练，帮助用户优化精力分配，提升工作表现和生活品质。

## 产品定位

- **目标用户**: 30-50岁中高阶职场人士、创业者和管理者
- **核心价值**: 提供真人教练般的AI精力管理服务
- **商业模式**: 订阅制(月费300元/年费2998元)

## 技术栈

### 前端
- **开发语言**: Swift 5.7+
- **UI框架**: SwiftUI
- **最低版本**: iOS 17.0
- **开发工具**: Xcode 14+

### 后端
- **开发语言**: Python 3.11+
- **Web框架**: FastAPI 0.100+
- **数据库**: PostgreSQL 15+
- **AI引擎**: OpenAI GPT-4 API

### 部署
- **云平台**: 阿里云 (ECS + RDS + OSS)

## 核心功能

### 1. AI教练对话
- 文字/语音多模态交互
- 3种教练人设可选(智者/伙伴/专家)
- 主动对话触发(晨间简报/晚间复盘)

### 2. 多源数据感知
- Apple Health数据集成(睡眠、心率、HRV)
- 日历和任务数据同步
- 对话式主观数据收集

### 3. 智能干预工具
- 引导式呼吸练习
- 专注计时器(番茄钟)
- 个性化精力建议

### 4. 精力预测
- 基于历史数据的精力状态预测
- 精力模式识别
- 关键时刻主动提醒

## 项目结构

```
PeakState-IOS/
├── 01PeakState产品文档v2.0.pdf    # 完整产品需求文档
├── 02核心竞争力构建方案.pdf        # 技术竞争力分析
├── 03技术实施文档.md              # 开发实施指南
├── 04UI原型图/                    # UI设计稿
├── PeakState/                     # iOS主项目(待创建)
│   ├── PeakState/                 # 源代码
│   │   ├── Models/               # 数据模型
│   │   ├── Views/                # 界面视图
│   │   ├── ViewModels/           # 视图模型
│   │   ├── Services/             # 业务服务
│   │   └── Utils/                # 工具类
│   └── PeakState.xcodeproj       # Xcode项目文件
└── Backend/                       # 后端服务(待创建)
    ├── app/                       # FastAPI应用
    ├── models/                    # 数据模型
    ├── api/                       # API路由
    └── requirements.txt           # Python依赖
```

## 开发计划

### 阶段1: 准备与设计 (1-3周)
- [x] 产品需求文档
- [x] 技术架构设计
- [x] UI/UX设计
- [ ] 开发环境搭建

### 阶段2: 核心功能开发 (4-10周)
- [ ] iOS项目初始化
- [ ] 入职流程实现
- [ ] AI对话界面
- [ ] HealthKit数据集成
- [ ] 后端API服务
- [ ] 主动触发机制

### 阶段3: 集成与测试 (11-14周)
- [ ] AI模型优化
- [ ] 干预工具开发
- [ ] 付费流程集成
- [ ] 内部测试

### 阶段4: 发布上线 (15-16周)
- [ ] App Store提交
- [ ] 用户反馈收集
- [ ] 持续优化迭代

## 快速开始

### 环境要求
- macOS 13.0+
- Xcode 14.0+
- Swift 5.7+
- iOS 17.0+ (目标设备)

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/kobwhatsup/PeakState.git
cd PeakState-IOS
```

2. 打开Xcode项目
```bash
open PeakState/PeakState.xcodeproj
```

3. 配置开发者账号
- 在Xcode中选择你的开发团队
- 配置Bundle Identifier

4. 运行项目
- 选择模拟器或真机
- 按 Cmd+R 运行

## 核心竞争力

### 数据护城河
- 构建用户"精力数字孪生"
- 多维度数据采集与分析
- 持续学习用户模式

### 算法护城河
- 专属精力预测模型
- 个性化推荐引擎
- 实时效果追踪优化

### 体验护城河
- "真人教练"般的交互
- 关键时刻主动干预
- 持续的价值交付

## 版本历史

### v1.0.0 (计划中)
- 基础对话功能
- HealthKit集成
- 入职流程
- 简单预测模型

## 贡献指南

欢迎提交Issue和Pull Request。

## 许可证

Copyright © 2025 PeakState Team. All rights reserved.

## 联系方式

- 产品负责人: KOB
- GitHub: https://github.com/kobwhatsup/PeakState
