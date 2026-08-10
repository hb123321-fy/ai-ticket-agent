import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
});

// 获取工单列表
export const getTickets = (userId: number = 1) =>
  api.get(`/tickets?user_id=${userId}`);

// 创建工单
export const createTicket = (data: any) =>
  api.post('/tickets', data, { params: { user_id: 1 } });

// Agent 处理工单
export const processTicket = (ticketId: number) =>
  api.post(`/tickets/${ticketId}/process`, {}, { params: { user_id: 1 } });

// 批准操作
export const approveTicket = (ticketId: number) =>
  api.post(`/tickets/${ticketId}/approve`, {}, { params: { user_id: 2 } });

// 查看审计
export const getAudit = (ticketId: number) =>
  api.get(`/tickets/${ticketId}/audit`, { params: { user_id: 2 } });

export default api;