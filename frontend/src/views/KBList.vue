<template>
  <div>
    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
      <h2>📚 知识库列表</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">+ 新建知识库</button>
    </div>

    <div class="kb-grid">
      <div v-for="kb in kbList" :key="kb.id" class="card kb-card" @click="goToDetail(kb.id)">
        <h3>{{ kb.name }}</h3>
        <p>{{ kb.description || '暂无描述' }}</p>
        <span class="tag">ID: {{ kb.id }}</span>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay">
      <div class="card modal">
        <h3>新建知识库</h3>
        <input v-model="newKB.name" placeholder="知识库名称" style="width:100%; margin:10px 0;">
        <input v-model="newKB.description" placeholder="描述" style="width:100%; margin-bottom:10px;">
        <button @click="createKB" class="btn btn-primary">确认创建</button>
        <button @click="showCreateModal = false" class="btn" style="margin-left:10px">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import request from '../../utils/request';

export default {
  data() {
    return {
      kbList: [],
      showCreateModal: false,
      newKB: { name: '', description: '' }
    };
  },
  mounted() {
    this.fetchKBList();
  },
  methods: {
    async fetchKBList() {
      const res = await request.get('/kb/list');
      this.kbList = res.data;
    },
    async createKB() {
      await request.post('/kb/create', this.newKB);
      this.showCreateModal = false;
      this.fetchKBList();
    },
    goToDetail(id) {
      this.$router.push(`/kb/${id}`);
    }
  }
};
</script>

<style scoped>
.kb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
.kb-card { cursor: pointer; transition: transform 0.2s; }
.kb-card:hover { transform: translateY(-5px); border: 1px solid #42b983; }
.modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; }
.modal { width: 400px; }
</style>