/**
 * 聊天状态管理
 * 使用Zustand管理对话列表和消息
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  Conversation,
  Message,
  SendMessageRequest,
  CreateConversationRequest,
  CoachType,
} from "../api";
import {
  sendMessage as apiSendMessage,
  createConversation as apiCreateConversation,
  getConversations as apiGetConversations,
  getConversationHistory as apiGetConversationHistory,
  deleteConversation as apiDeleteConversation,
} from "../api";

interface ChatState {
  // 状态
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;

  // 动作
  sendMessage: (content: string, metadata?: any) => Promise<void>;
  createConversation: (coachType: CoachType, title?: string) => Promise<string>;
  loadConversations: () => Promise<void>;
  loadConversationHistory: (conversationId: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  setCurrentConversation: (conversationId: string | null) => void;
  clearError: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // 初始状态
      conversations: [],
      currentConversationId: null,
      messages: [],
      isLoading: false,
      isSending: false,
      error: null,

      // 发送消息
      sendMessage: async (content: string, metadata?: any) => {
        const { currentConversationId } = get();

        if (!currentConversationId) {
          set({ error: "请先选择或创建对话" });
          return;
        }

        set({ isSending: true, error: null });

        // 乐观更新：立即添加用户消息到界面
        const userMessage: Message = {
          id: `temp-${Date.now()}`,
          conversation_id: currentConversationId,
          role: "user",
          content,
          timestamp: new Date().toISOString(),
          metadata,
        };

        set((state) => ({
          messages: [...state.messages, userMessage],
        }));

        try {
          const request: SendMessageRequest = {
            conversation_id: currentConversationId,
            content,
            metadata,
          };

          const response = await apiSendMessage(request);

          // 更新消息列表：替换临时用户消息和添加助手回复
          set((state) => ({
            messages: [
              ...state.messages.filter((m) => m.id !== userMessage.id),
              response.user_message,
              response.assistant_message,
            ],
          }));

          // 更新对话的最后消息时间
          set((state) => ({
            conversations: state.conversations.map((conv) =>
              conv.id === currentConversationId
                ? {
                    ...conv,
                    last_message_at: response.assistant_message.timestamp,
                  }
                : conv
            ),
          }));
        } catch (error: any) {
          // 移除乐观添加的用户消息
          set((state) => ({
            messages: state.messages.filter((m) => m.id !== userMessage.id),
          }));

          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            "发送消息失败";
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isSending: false });
        }
      },

      // 创建新对话
      createConversation: async (coachType: CoachType, title?: string) => {
        set({ isLoading: true, error: null });
        try {
          const request: CreateConversationRequest = {
            coach_type: coachType,
            title,
          };

          const conversation = await apiCreateConversation(request);

          set((state) => ({
            conversations: [conversation, ...state.conversations],
            currentConversationId: conversation.id,
            messages: [],
          }));

          return conversation.id;
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            "创建对话失败";
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // 加载对话列表
      loadConversations: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiGetConversations();
          // 将ConversationListItem转换为Conversation格式
          const conversations: Conversation[] = response.conversations.map(item => ({
            id: item.conversation_id,
            title: item.title || "新对话",
            created_at: item.created_at,
            updated_at: item.updated_at,
            message_count: item.message_count,
            last_message_at: item.updated_at
          }));
          set({ conversations });
        } catch (error: any) {
          console.error("Load conversations error:", error);
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            "加载对话列表失败";
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // 加载对话历史消息
      loadConversationHistory: async (conversationId: string) => {
        set({ isLoading: true, error: null, currentConversationId: conversationId });
        try {
          const messages = await apiGetConversationHistory(conversationId);
          set({ messages });
        } catch (error: any) {
          console.error("Load conversation history error:", error);
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            "加载对话历史失败";
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // 删除对话
      deleteConversation: async (conversationId: string) => {
        set({ isLoading: true, error: null });
        try {
          await apiDeleteConversation(conversationId);

          set((state) => {
            const newConversations = state.conversations.filter(
              (conv) => conv.id !== conversationId
            );
            const newCurrentId =
              state.currentConversationId === conversationId
                ? null
                : state.currentConversationId;

            return {
              conversations: newConversations,
              currentConversationId: newCurrentId,
              messages: newCurrentId ? state.messages : [],
            };
          });
        } catch (error: any) {
          console.error("Delete conversation error:", error);
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            "删除对话失败";
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // 设置当前对话
      setCurrentConversation: (conversationId: string | null) => {
        set({ currentConversationId: conversationId });
        if (conversationId) {
          get().loadConversationHistory(conversationId);
        } else {
          set({ messages: [] });
        }
      },

      // 清除错误
      clearError: () => {
        set({ error: null });
      },

      // 清除消息（用于切换对话或退出登录）
      clearMessages: () => {
        set({ messages: [], currentConversationId: null });
      },
    }),
    {
      name: "peakstate-chat", // localStorage key
      partialize: (state) => ({
        // 只持久化对话列表和当前对话ID，不持久化消息和状态
        conversations: state.conversations,
        currentConversationId: state.currentConversationId,
      }),
    }
  )
);
