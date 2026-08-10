<template>
  <div style="max-width: 900px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif;">
    <h1 style="color: #2c3e50; border-bottom: 3px solid #4CAF50; padding-bottom: 10px;">
      🤖 AI 研发支持工单
    </h1>

    <!-- 创建工单卡片 -->
    <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      <h3 style="margin-top: 0; color: #2c3e50;">📝 创建工单</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <input v-model="newTicket.title" placeholder="标题 *" style="padding: 10px; border: 1px solid #ddd; border-radius: 6px; grid-column: span 2;" />
        <textarea v-model="newTicket.description" placeholder="描述 *" rows="3" style="padding: 10px; border: 1px solid #ddd; border-radius: 6px; grid-column: span 2;"></textarea>
        <input v-model="newTicket.system" placeholder="所属系统" style="padding: 10px; border: 1px solid #ddd; border-radius: 6px;" />
        <select v-model="newTicket.environment" style="padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
          <option value="开发">开发</option>
          <option value="测试">测试</option>
          <option value="生产">生产</option>
        </select>
      </div>
      <button @click="handleCreateTicket" style="margin-top: 12px; padding: 10px 24px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">
        ✅ 提交工单
      </button>
    </div>

    <!-- 工单列表 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 16px 0;">
      <h3 style="margin: 0; color: #2c3e50;">📋 工单列表</h3>
      <button @click="loadTickets" style="padding: 6px 16px; background: #2196F3; color: white; border: none; border-radius: 6px; cursor: pointer;">🔄 刷新</button>
    </div>

    <div v-if="loading" style="text-align: center; padding: 40px; color: #999;">加载中...</div>
    <div v-else-if="tickets.length === 0" style="text-align: center; padding: 40px; color: #999;">暂无工单</div>
    <div v-else>
      <div v-for="ticket in tickets" :key="ticket.id" style="background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="font-size: 16px; color: #2c3e50;">#{{ ticket.id }} {{ ticket.title }}</strong>
          <span :style="{ 
            background: ticket.status === 'open' ? '#e8f5e9' : '#fff3e0', 
            color: ticket.status === 'open' ? '#2e7d32' : '#e65100',
            padding: '2px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 'bold'
          }">{{ ticket.status }}</span>
        </div>
        <div style="color: #555; font-size: 14px; margin: 8px 0;">{{ ticket.description }}</div>
        <div style="font-size: 12px; color: #999; margin-bottom: 10px;">
          🖥️ {{ ticket.system || '未指定' }} | 🌍 {{ ticket.environment }} | 🕐 {{ ticket.created_at?.slice(0, 10) }}
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button @click="handleProcess(ticket.id)" style="padding: 6px 14px; background: #2196F3; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">
            🤖 Agent处理
          </button>
          <button @click="handleApprove(ticket.id)" style="padding: 6px 14px; background: #FF9800; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">
            ✅ 批准
          </button>
          <button @click="handleAudit(ticket.id)" style="padding: 6px 14px; background: #9C27B0; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">
            📋 审计
          </button>
        </div>
        <div v-if="agentResult[ticket.id]" style="margin-top: 10px; padding: 12px; background: #f5f5f5; border-radius: 6px; font-size: 13px; white-space: pre-wrap; border-left: 3px solid #2196F3;">
          <strong>🤖 Agent:</strong> {{ agentResult[ticket.id] }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getTickets, createTicket, processTicket, approveTicket, getAudit } from '../api';

const tickets = ref<any[]>([]);
const loading = ref(false);
const agentResult = ref<Record<number, string>>({});

const newTicket = ref({
  title: '',
  description: '',
  system: '',
  environment: '测试',
});

const loadTickets = async () => {
  loading.value = true;
  try {
    const res = await getTickets(1);
    tickets.value = res.data;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const handleCreateTicket = async () => {
  if (!newTicket.value.title || !newTicket.value.description) {
    alert('标题和描述不能为空');
    return;
  }
  try {
    await createTicket(newTicket.value);
    newTicket.value = { title: '', description: '', system: '', environment: '测试' };
    await loadTickets();
  } catch (e) {
    console.error(e);
  }
};

const handleProcess = async (id: number) => {
  try {
    const res = await processTicket(id);
    agentResult.value[id] = JSON.stringify(res.data, null, 2);
    await loadTickets();
  } catch (e) {
    console.error(e);
  }
};

const handleApprove = async (id: number) => {
  try {
    const res = await approveTicket(id);
    agentResult.value[id] = res.data.message || '已批准';
    await loadTickets();
  } catch (e) {
    console.error(e);
  }
};

const handleAudit = async (id: number) => {
  try {
    const res = await getAudit(id);
    alert(JSON.stringify(res.data, null, 2));
  } catch (e) {
    console.error(e);
  }
};

onMounted(loadTickets);
</script>