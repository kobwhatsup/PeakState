/**
 * 聊天API接口
 * 发送消息、获取对话历史、管理对话
 */

import { apiClient } from "./client";
import type {
  SendMessageRequest,
  SendMessageResponse,
  Conversation,
  ConversationListResponse,
  Message,
  CreateConversationRequest,
} from "./types";

// ========== 发送消息 ==========

export const sendMessage = async (
  data: SendMessageRequest
): Promise<SendMessageResponse> => {
  const response = await apiClient.post<SendMessageResponse>(
    "/chat/send",
    data
  );
  return response.data;
};

// ========== 创建新对话 ==========

export const createConversation = async (
  data?: CreateConversationRequest
): Promise<Conversation> => {
  const response = await apiClient.post<Conversation>("/chat/new", data || {});
  return response.data;
};

// ========== 获取所有对话列表 ==========

export const getConversations = async (
  page: number = 1,
  pageSize: number = 20
): Promise<ConversationListResponse> => {
  const response = await apiClient.get<ConversationListResponse>(
    "/chat/conversations",
    { params: { page, page_size: pageSize } }
  );
  return response.data;
};

// ========== 获取指定对话的消息历史 ==========

export const getConversationHistory = async (
  conversationId: string
): Promise<Message[]> => {
  const response = await apiClient.get<Message[]>(
    `/chat/history/${conversationId}`
  );
  return response.data;
};

// ========== 删除对话 ==========

export const deleteConversation = async (
  conversationId: string
): Promise<void> => {
  await apiClient.delete(`/chat/${conversationId}`);
};

// ========== 调试：查看AI路由信息 ==========

export const debugRouting = async (message: string): Promise<any> => {
  const response = await apiClient.post("/chat/debug/routing", { message });
  return response.data;
};
