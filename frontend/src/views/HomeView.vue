<template>
  <div class="home-dashboard">
    <div class="welcome-header">
      <h1>欢迎来到 <span class="brand-gradient">RAGDemo</span></h1>
      <p class="subtitle">构建您的专属知识库与智能问答系统</p>
    </div>

    <section class="dashboard-section">
      <div class="section-title">
        <span class="icon-box kb-icon">📚</span>
        <h2>知识库</h2>
      </div>
      
      <div class="card-grid">
        <div v-for="kb in kbList" :key="kb.id" class="dashboard-card" @click="$router.push(`/kb/${kb.id}`)">
          <div class="card-top">
            <div class="card-avatar kb-avatar">📖</div>
            <div class="card-meta">
              <h3>{{ kb.name }}</h3>
              <span class="file-count">ID: {{ kb.id }}</span>
            </div>
          </div>
          <div class="card-bottom">
            <p class="date">{{ formatDate(kb.created_at) }}</p>
          </div>
        </div>

        <div class="dashboard-card action-card" @click="$router.push('/kb')">
          <div class="action-content">
            <span class="plus-icon">+</span>
            <span>管理/新建</span>
          </div>
        </div>
      </div>
    </section>

    <section class="dashboard-section">
      <div class="section-title">
        <span class="icon-box chat-icon">💬</span>
        <h2>最近对话</h2>
      </div>
      
      <div class="card-grid">
        <div 
          v-for="session in sessionList" 
          :key="session.id" 
          class="dashboard-card" 
          @click="goToChat(session.id)"
        >
          <div class="card-top">
            <div class="card-avatar chat-avatar">🤖</div>
            <div class="card-meta">
              <h3 :title="session.title">{{ session.title || '新对话' }}</h3>
              <span class="file-count">历史记录</span>
            </div>
          </div>
          <div class="card-bottom">
            <p class="date">{{ formatDate(session.created_at) }}</p>
          </div>
        </div>

        <div class="dashboard-card action-card" @click="goToChat(null)">
          <div class="action-content">
             <span class="plus-icon" style="font-size: 1.5rem">💬</span>
            <span>+ 开始新对话</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import request from '../../utils/request';

export default {
  data() {
    return {
      kbList: [],
      sessionList: []
    };
  },
  mounted() {
    this.fetchKBs();
    this.fetchSessions(); 
  },
  methods: {
    async fetchKBs() {
      try {
        const res = await request.get('/kb/list');
        this.kbList = res.data.slice(0, 3);
      } catch (e) {
        console.error(e);
      }
    },
    // 🟢 新增：获取最近会话
    async fetchSessions() {
      try {
        const res = await request.get('/sessions');
        // 取最近 3 个展示
        this.sessionList = res.data.slice(0, 3);
      } catch (e) {
        console.error("加载会话失败", e);
      }
    },
    // 🟢 新增：跳转逻辑 (带参数)
    goToChat(sessionId) {
      if (sessionId) {
        // 如果点击了具体会话，传参过去
        this.$router.push({ path: '/chat', query: { session_id: sessionId } });
      } else {
        // 如果点击新建，直接去聊天页
        this.$router.push('/chat');
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      // 优化时间显示格式
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }
};
</script>

<style scoped>
/* 样式保持不变，直接复用之前的 CSS 即可 */
.home-dashboard { max-width: 1200px; margin: 0 auto; padding: 20px; }
.welcome-header { margin-bottom: 50px; padding-top: 20px; }
.welcome-header h1 { font-size: 2.8rem; margin: 0; color: #333; }
.brand-gradient { background: linear-gradient(90deg, #42b983, #1976d2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.subtitle { color: #666; font-size: 1.1rem; margin-top: 10px; }
.dashboard-section { margin-bottom: 50px; }
.section-title { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; }
.section-title h2 { font-size: 1.4rem; margin: 0; font-weight: 600; color: #2c3e50; }
.icon-box { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 1.2rem; }
.kb-icon { color: #2e7d32; }
.chat-icon { color: #1976d2; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.dashboard-card { background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.3s ease; display: flex; flex-direction: column; justify-content: space-between; height: 140px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.dashboard-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); border-color: #42b983; }
.card-top { display: flex; gap: 15px; align-items: flex-start; }
.card-avatar { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
.kb-avatar { background: #e8f5e9; color: #2e7d32; }
.chat-avatar { background: #e3f2fd; color: #1565c0; }
/* 限制标题长度，防止溢出 */
.card-meta h3 { margin: 0 0 5px 0; font-size: 1.1rem; color: #333; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.file-count { font-size: 0.85rem; color: #888; background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
.card-bottom { border-top: 1px solid #f9f9f9; padding-top: 10px; margin-top: 10px; }
.date { font-size: 0.8rem; color: #aaa; margin: 0; text-align: right; }
.action-card { background: #f8f9fa; border: 1px dashed #ddd; align-items: center; justify-content: center; }
.action-content { text-align: center; color: #666; font-weight: 500; }
.plus-icon { display: block; font-size: 2rem; margin-bottom: 5px; color: #aaa; }
.action-card:hover .plus-icon { color: #42b983; }
</style>