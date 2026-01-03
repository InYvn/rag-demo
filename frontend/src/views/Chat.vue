<template>
  <div class="chat-layout">

    <aside class="sidebar left-sidebar">
      <div class="sidebar-header">
        <button @click="startNewChat" class="btn btn-primary full-width">
          <span class="plus-icon">+</span> 新建对话
        </button>
      </div>

      <div class="session-list">
        <div class="list-header">历史记录</div>
        <div v-for="s in sessionList" :key="s.id" class="session-item" :class="{ active: s.id === currentSessionId }"
          @click="loadSession(s.id)">
          <span class="icon">💬</span>
          <span class="title">{{ s.title || '无标题会话' }}</span>
        </div>
      </div>
    </aside>

    <main class="chat-center">
      <div class="chat-header">
        <span class="header-title">{{ currentSessionTitle }}</span>
        <span class="header-model-tag">GLM-4.5-Flash</span>
      </div>

      <div class="chat-history" ref="chatBox">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">👋</div>
          <h3>你好！我是你的 RAG 智能助手</h3>
          <p>请在右侧选择知识库，然后开始提问吧。</p>
        </div>

        <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="bubble-content">
            <div class="bubble" v-html="renderMarkdown(msg.content)"></div>
            <div v-if="msg.role === 'assistant' && msg.kb_id" class="msg-meta">
              KB: {{ getKBName(msg.kb_id) }}
            </div>
          </div>
        </div>

        <div v-if="loading" class="msg-row assistant">
          <div class="avatar">🤖</div>
          <div class="bubble loading">正在思考...</div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <input v-model="question" @keyup.enter="send" placeholder="输入您的问题..." :disabled="loading">
          <button @click="send" class="btn-send" :disabled="loading || !question.trim()">
            ➤
          </button>
        </div>
      </div>
    </main>

    <aside class="sidebar right-sidebar">
      <div class="settings-header">
        <h3>⚙️ 参数配置</h3>
      </div>

      <div class="settings-body">
        <div class="form-group">
          <label class="form-label">📚 引用知识库</label>
          <select v-model="selectedKbId" class="form-select">
            <option :value="null" disabled>请选择知识库</option>
            <option v-for="kb in kbList" :key="kb.id" :value="kb.id">{{ kb.name }}</option>
          </select>
          <p class="form-hint">选择后，AI 将基于该库回答。</p>
        </div>

        <div class="divider"></div>

        <div class="form-group">
          <div class="label-row">
            <label class="form-label">🌡️ 随机性 (Temperature)</label>
            <span class="val-tag">{{ temperature }}</span>
          </div>
          <input type="range" v-model.number="temperature" min="0" max="1" step="0.1" class="form-range">
          <p class="form-hint">
            0: 精确严谨 (适合知识问答)<br>
            1: 创意发散 (适合闲聊)
          </p>
        </div>

        <div class="divider"></div>

        <div class="form-group">
          <div class="label-row">
            <label class="form-label">🔗 引用片段数 (Top K)</label>
            <span class="val-tag">{{ topK }}</span>
          </div>
          <input type="range" v-model.number="topK" min="1" max="10" step="1" class="form-range">
          <p class="form-hint">每次参考多少段文档内容。</p>
        </div>
      </div>
    </aside>

  </div>
</template>

<script>
import request from '../../utils/request';
import { marked } from 'marked';

export default {
  data() {
    return {
      kbList: [],
      sessionList: [],
      messages: [],
      selectedKbId: null,
      currentSessionId: null,
      question: '',
      loading: false,
      temperature: 0.1,
      topK: 3
    };
  },
  computed: {
    currentSessionTitle() {
      const s = this.sessionList.find(i => i.id === this.currentSessionId);
      return s ? s.title : '新对话';
    }
  },
  async mounted() {
    await this.fetchKBs();
    await this.fetchSessions();
    const routeSessionId = this.$route.query.session_id;
    if (routeSessionId) {
      await this.loadSession(routeSessionId);
    } else if (this.kbList.length > 0) {
      this.selectedKbId = this.kbList[0].id; // 默认选中第一个KB
    }
  },
  methods: {
    renderMarkdown(text) { return marked.parse(text || ''); },

    getKBName(id) {
      const kb = this.kbList.find(k => k.id === id);
      return kb ? kb.name : '未知知识库';
    },

    async fetchKBs() {
      const res = await request.get('/kb/list');
      this.kbList = res.data;
    },

    async fetchSessions() {
      const res = await request.get('/sessions');
      this.sessionList = res.data;
    },

    startNewChat() {
      this.currentSessionId = null;
      this.messages = [];

      if (this.$route.query.session_id) {
        this.$router.push('/chat');
      }
    },

    async loadSession(sessionId) {
      this.currentSessionId = sessionId;
      const res = await request.get(`/sessions/${sessionId}/messages`);
      this.messages = res.data;
      this.scrollToBottom();
    },

    async send() {
      if (!this.question.trim()) return;
      if (!this.selectedKbId) return alert("请先在右侧选择一个知识库！");

      const q = this.question;
      this.messages.push({ role: 'user', content: q });
      this.question = '';
      this.loading = true;
      this.scrollToBottom();

      try {
        const res = await request.post('/chat', {
          question: q,
          kb_id: this.selectedKbId,
          session_id: this.currentSessionId,
          temperature: this.temperature,
          top_k: this.topK
        });

        this.messages.push({ role: 'assistant', content: res.data.answer, kb_id: this.selectedKbId });

        if (!this.currentSessionId) {
          this.currentSessionId = res.data.session_id;
          await this.fetchSessions();
        }
      } catch (e) {
        this.messages.push({ role: 'assistant', content: '❌ 出错了: ' + e.message });
      } finally {
        this.loading = false;
        this.scrollToBottom();
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const box = this.$refs.chatBox;
        if (box) box.scrollTop = box.scrollHeight;
      });
    }
  }
};
</script>

<style scoped>
/* --- 布局核心 --- */
.chat-layout {
  display: flex;
  height: calc(100vh - 60px);
  /* 减去顶部导航栏高度 */
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
}

/* 通用侧边栏 */
.sidebar {
  background: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

/* 左侧栏 */
.left-sidebar {
  width: 260px;
  border-right: 1px solid #eee;
}

/* 右侧栏 */
.right-sidebar {
  width: 300px;
  border-left: 1px solid #eee;
  background: #fff;
}

/* 中间栏 */
.chat-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}

/* --- 左侧样式 --- */
.sidebar-header {
  margin-bottom: 20px;
}

.full-width {
  width: 100%;
  justify-content: center;
}

.session-list .list-header {
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 10px;
  font-weight: 600;
}

.session-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #444;
  transition: 0.2s;
}

.session-item:hover {
  background: #f5f5f5;
}

.session-item.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.session-item .icon {
  margin-right: 10px;
  font-size: 1.1rem;
}

.session-item .title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.95rem;
}

/* --- 右侧样式 --- */
.settings-header h3 {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  color: #333;
}

.settings-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #555;
}

.form-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  background: white;
}

.form-range {
  width: 100%;
  cursor: pointer;
}

.form-hint {
  font-size: 0.8rem;
  color: #999;
  margin: 0;
  line-height: 1.4;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.val-tag {
  background: #eee;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-family: monospace;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 5px 0;
}

/* --- 中间聊天样式 --- */
.chat-header {
  padding: 15px 25px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
}

.header-title {
  font-weight: bold;
  font-size: 1.1rem;
}

.header-model-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.chat-history {
  flex: 1;
  padding: 20px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.msg-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.assistant .avatar {
  background: #e3f2fd;
}

.user .avatar {
  background: #e8f5e9;
}

.bubble-content {
  max-width: 75%;
}

.bubble {
  padding: 15px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 0.95rem;
}

.assistant .bubble {
  background: #f9f9f9;
  color: #333;
}

.user .bubble {
  background: #42b983;
  color: white;
}

.assistant .bubble.loading {
  font-style: italic;
  color: #999;
}

.msg-meta {
  font-size: 0.75rem;
  color: #ccc;
  margin-top: 5px;
  text-align: right;
}

.empty-state {
  text-align: center;
  margin-top: 100px;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

/* 输入框区域 */
.input-area {
  padding: 20px 40px;
  background: #fff;
  /* border-top: 1px solid #eee; */
}

.input-wrapper {
  display: flex;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 5px;
  border: 1px solid transparent;
  transition: 0.3s;
}

.input-wrapper:focus-within {
  background: #fff;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 15px;
  font-size: 1rem;
  outline: none;
}

.btn-send {
  background: #42b983;
  color: white;
  border: none;
  width: 45px;
  height: 45px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  margin: 3px;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-send:hover:not(:disabled) {
  background: #3aa876;
}

.btn-send:disabled {
  background: #ddd;
  cursor: not-allowed;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}
</style>