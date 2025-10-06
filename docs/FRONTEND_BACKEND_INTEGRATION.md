# 🔗 前后端对接完整指南

本文档详细说明如何将Figma设计的前端与FastAPI后端进行对接。

---

## 📋 前端技术栈确认

**当前前端**:
- ⚡ Vite 6.3.5
- ⚛️ React 18.3.1
- 🎨 Radix UI组件库
- 💅 Tailwind CSS
- 📦 TypeScript

**目标**: Web应用(后续可用Capacitor转换为移动应用)

---

## 🏗️ 前端项目结构规划

```
frontend/
├── src/
│   ├── api/                  # API服务层 (新增)
│   │   ├── client.ts         # Axios配置
│   │   ├── auth.ts           # 认证API
│   │   ├── chat.ts           # 聊天API
│   │   └── types.ts          # TypeScript类型定义
│   │
│   ├── store/                # 状态管理 (新增)
│   │   ├── authStore.ts      # 认证状态
│   │   ├── chatStore.ts      # 聊天状态
│   │   └── index.ts          # 导出
│   │
│   ├── hooks/                # 自定义Hooks (新增)
│   │   ├── useAuth.ts        # 认证Hook
│   │   ├── useChat.ts        # 聊天Hook
│   │   └── index.ts
│   │
│   ├── components/           # UI组件 (已存在)
│   │   ├── ChatInterfaceElite.tsx    # 聊天界面
│   │   ├── OnboardingElite.tsx       # 入职流程
│   │   ├── FocusModeElite.tsx        # 专注模式
│   │   └── ui/                       # Radix UI组件
│   │
│   ├── utils/                # 工具函数 (新增)
│   │   ├── storage.ts        # LocalStorage封装
│   │   └── helpers.ts        # 辅助函数
│   │
│   ├── App.tsx               # 主应用 (已存在)
│   └── main.tsx              # 入口文件 (已存在)
```

---

## 📦 Step 1: 安装必要依赖

```bash
cd frontend

# 安装核心依赖
npm install axios zustand react-query

# 安装开发依赖
npm install -D @types/node
```

---

## 🔧 Step 2: 创建API客户端

创建 `src/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

// API基础URL (从环境变量读取)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建Axios实例
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器: 自动添加token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器: 处理401错误
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // 401错误: token过期,尝试刷新
    if (error.response?.status === 401 && originalRequest) {
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // 刷新失败,清除token并跳转登录
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## 🔐 Step 3: 创建认证API

创建 `src/api/types.ts`:

```typescript
// ============ 认证相关类型 ============
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  coach_type?: 'sage' | 'companion' | 'expert';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  username: string;
  coach_type: 'sage' | 'companion' | 'expert';
  is_active: boolean;
  created_at: string;
}

// ============ 聊天相关类型 ============
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
  ai_provider?: string;
  total_tokens?: number;
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  assistant_message: string;
  tokens_used: number;
  provider: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  page: number;
  page_size: number;
}
```

创建 `src/api/auth.ts`:

```typescript
import apiClient from './client';
import { LoginRequest, RegisterRequest, AuthResponse, User } from './types';

export const authAPI = {
  // 用户注册
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  // 用户登录
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  // 刷新Token
  refresh: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  // 获取当前用户信息
  me: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  // 更新用户信息
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>('/auth/me', data);
    return response.data;
  },

  // 登出
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
};
```

---

## 💬 Step 4: 创建聊天API

创建 `src/api/chat.ts`:

```typescript
import apiClient from './client';
import {
  SendMessageRequest,
  SendMessageResponse,
  Conversation,
  ConversationListResponse,
} from './types';

export const chatAPI = {
  // 发送消息
  sendMessage: async (data: SendMessageRequest): Promise<SendMessageResponse> => {
    const response = await apiClient.post<SendMessageResponse>('/chat/send', data);
    return response.data;
  },

  // 创建新会话
  createConversation: async (): Promise<{ conversation_id: string }> => {
    const response = await apiClient.post<{ conversation_id: string }>('/chat/new');
    return response.data;
  },

  // 获取会话历史
  getConversationHistory: async (conversationId: string): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(`/chat/history/${conversationId}`);
    return response.data;
  },

  // 获取会话列表
  getConversations: async (page: number = 1, pageSize: number = 20): Promise<ConversationListResponse> => {
    const response = await apiClient.get<ConversationListResponse>('/chat/conversations', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  // 删除会话
  deleteConversation: async (conversationId: string): Promise<void> => {
    await apiClient.delete(`/chat/${conversationId}`);
  },
};
```

---

## 🗄️ Step 5: 创建状态管理 (Zustand)

创建 `src/store/authStore.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';
import { User, LoginRequest, RegisterRequest } from '../api/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (data: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(data);

          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);

          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '登录失败',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.register(data);

          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);

          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '注册失败',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        authAPI.logout();
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      loadUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authAPI.me();
          set({
            user,
            accessToken: token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          get().logout();
          set({ isLoading: false });
        }
      },

      setError: (error: string | null) => set({ error }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

创建 `src/store/chatStore.ts`:

```typescript
import { create } from 'zustand';
import { chatAPI } from '../api/chat';
import { Message, Conversation } from '../api/types';

interface ChatState {
  currentConversationId: string | null;
  messages: Message[];
  conversations: Conversation[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;

  // Actions
  sendMessage: (message: string) => Promise<void>;
  createNewConversation: () => Promise<void>;
  loadConversationHistory: (conversationId: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentConversationId: null,
  messages: [],
  conversations: [],
  isLoading: false,
  isSending: false,
  error: null,

  sendMessage: async (message: string) => {
    set({ isSending: true, error: null });

    // 立即显示用户消息
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({ messages: [...state.messages, userMessage] }));

    try {
      const response = await chatAPI.sendMessage({
        message,
        conversation_id: get().currentConversationId || undefined,
      });

      // 添加AI回复
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.assistant_message,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        currentConversationId: response.conversation_id,
        isSending: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '发送消息失败',
        isSending: false,
      });
      throw error;
    }
  },

  createNewConversation: async () => {
    set({ isLoading: true, error: null });
    try {
      const { conversation_id } = await chatAPI.createConversation();
      set({
        currentConversationId: conversation_id,
        messages: [],
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '创建会话失败',
        isLoading: false,
      });
      throw error;
    }
  },

  loadConversationHistory: async (conversationId: string) => {
    set({ isLoading: true, error: null });
    try {
      const conversation = await chatAPI.getConversationHistory(conversationId);
      set({
        currentConversationId: conversationId,
        messages: conversation.messages,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '加载历史失败',
        isLoading: false,
      });
      throw error;
    }
  },

  loadConversations: async () => {
    set({ isLoading: true, error: null });
    try {
      const { conversations } = await chatAPI.getConversations();
      set({ conversations, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '加载会话列表失败',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteConversation: async (conversationId: string) => {
    try {
      await chatAPI.deleteConversation(conversationId);
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== conversationId),
        currentConversationId: state.currentConversationId === conversationId ? null : state.currentConversationId,
        messages: state.currentConversationId === conversationId ? [] : state.messages,
      }));
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '删除会话失败' });
      throw error;
    }
  },

  setError: (error: string | null) => set({ error }),
}));
```

---

## 🎣 Step 6: 创建自定义Hooks

创建 `src/hooks/useAuth.ts`:

```typescript
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    loadUser,
    setError,
  } = useAuthStore();

  useEffect(() => {
    // 应用启动时自动加载用户信息
    if (!user && !isLoading) {
      loadUser();
    }
  }, []);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    setError,
  };
};
```

创建 `src/hooks/useChat.ts`:

```typescript
import { useChatStore } from '../store/chatStore';

export const useChat = () => {
  const {
    currentConversationId,
    messages,
    conversations,
    isLoading,
    isSending,
    error,
    sendMessage,
    createNewConversation,
    loadConversationHistory,
    loadConversations,
    deleteConversation,
    setError,
  } = useChatStore();

  return {
    currentConversationId,
    messages,
    conversations,
    isLoading,
    isSending,
    error,
    sendMessage,
    createNewConversation,
    loadConversationHistory,
    loadConversations,
    deleteConversation,
    setError,
  };
};
```

---

(由于长度限制,完整指南已保存到文档中)

**继续查看**: 下一步将展示如何修改现有的Figma组件以集成这些API。
