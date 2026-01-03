<template>
  <div class="kb-detail-container">
    <header class="page-header">
      <div class="left">
        <button @click="$router.push('/kb')" class="btn-back">← 返回列表</button>
        <h2>📂 知识库详情 <span class="tag">ID: {{ kbId }}</span></h2>
      </div>
      <div class="right">
        <button @click="showUploadModal = true" class="btn btn-primary btn-sm">
          + 新增文件
        </button>
      </div>
    </header>

    <div class="card table-card">
      <div class="table-header">
        <h3>文件列表 ({{ files.length }})</h3>
        <button @click="fetchFiles" class="btn-icon" title="刷新">🔄</button>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th width="50%">文件名</th>
            <th>上传时间</th>
            <th>状态</th>
            <th>解析引擎</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="files.length === 0">
            <td colspan="4" class="empty-text">暂无文件，请点击右上角上传</td>
          </tr>
          <tr v-for="file in files" :key="file.id">
            <td class="file-name">
              <span class="icon">📄</span> {{ file.filename }}
            </td>
            <td class="text-muted">{{ formatDate(file.upload_time) }}</td>
            <td>
              <span class="status-badge success">✅ {{ file.status || '已解析' }}</span>
            </td>
            <td><span class="engine-tag">General</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📤 上传新文件</h3>
          <button @click="showUploadModal = false" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <div class="upload-zone" :class="{ 'dragging': isDragging }"
               @dragover.prevent="isDragging = true"
               @dragleave.prevent="isDragging = false"
               @drop.prevent="handleDrop">
            
            <input type="file" ref="fileInput" @change="handleFileSelect" accept=".pdf" style="display:none">
            
            <div v-if="!file" class="upload-placeholder" @click="$refs.fileInput.click()">
              <div class="icon-cloud">☁️</div>
              <p>点击或拖拽 PDF 文件到此处</p>
              <span class="hint">支持 .pdf 格式</span>
            </div>

            <div v-else class="file-preview">
              <span class="file-icon">📄</span>
              <span class="file-name">{{ file.name }}</span>
              <button @click="file = null" class="btn-remove" v-if="!uploading">删除</button>
            </div>
          </div>

          <div v-if="uploadStatus" :class="['status-message', uploadStatusClass]">
            {{ uploadStatus }}
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showUploadModal = false" class="btn btn-text" :disabled="uploading">取消</button>
          <button @click="upload" class="btn btn-primary" :disabled="!file || uploading">
            {{ uploading ? '上传解析中...' : '开始上传' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from '../../utils/request';

export default {
  data() {
    return {
      kbId: this.$route.params.id,
      files: [],
      showUploadModal: false,
      file: null,
      uploading: false,
      uploadStatus: '',
      isDragging: false
    };
  },
  mounted() {
    this.fetchFiles();
  },
  computed: {
    uploadStatusClass() {
      if (this.uploadStatus.includes('成功')) return 'success';
      if (this.uploadStatus.includes('失败')) return 'error';
      return 'info';
    }
  },
  methods: {
    // 获取文件列表
    async fetchFiles() {
      try {
        const res = await request.get(`/kb/${this.kbId}/files`);
        this.files = res.data;
      } catch (e) {
        console.error("加载文件失败", e);
      }
    },
    // 日期格式化
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString();
    },
    // 处理文件选择
    handleFileSelect(e) {
      this.file = e.target.files[0];
      this.uploadStatus = '';
    },
    handleDrop(e) {
      this.isDragging = false;
      const droppedFiles = e.dataTransfer.files;
      if (droppedFiles.length > 0 && droppedFiles[0].type === 'application/pdf') {
        this.file = droppedFiles[0];
        this.uploadStatus = '';
      } else {
        alert("请上传 PDF 文件");
      }
    },
    // 上传逻辑
    async upload() {
      if (!this.file) return;
      
      this.uploading = true;
      this.uploadStatus = '⏳ 正在上传并构建索引，请稍候...';
      
      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('kb_id', this.kbId);

      try {
        await request.post('/upload', formData);
        this.uploadStatus = '✅ 上传解析成功！';
        
        // 上传成功后：刷新列表，1秒后关闭弹窗
        await this.fetchFiles();
        setTimeout(() => {
          this.showUploadModal = false;
          this.file = null;
          this.uploadStatus = '';
        }, 1500);
        
      } catch (e) {
        this.uploadStatus = '❌ 上传失败: ' + (e.response?.data?.detail || '服务器错误');
      } finally {
        this.uploading = false;
      }
    }
  }
};
</script>

<style scoped>
/* 页面布局 */
.kb-detail-container { max-width: 1200px; margin: 0 auto; }

/* 顶部栏 */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; font-size: 1.5rem; color: #2c3e50; display: flex; align-items: center; gap: 10px; }
.btn-back { border: none; background: none; color: #666; cursor: pointer; font-size: 0.9rem; margin-right: 10px; }
.btn-back:hover { color: #42b983; }
.tag { font-size: 0.8rem; background: #eee; padding: 2px 8px; border-radius: 4px; color: #666; font-weight: normal; }

/* 表格卡片 */
.table-card { min-height: 400px; padding: 0; }
.table-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.table-header h3 { margin: 0; font-size: 1.1rem; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 1.2rem; }

/* 数据表格 */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 15px 20px; background: #f8f9fa; color: #666; font-weight: 600; font-size: 0.9rem; }
.data-table td { padding: 15px 20px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }
.data-table tr:hover { background-color: #fcfcfc; }
.file-name { font-weight: 500; color: #2c3e50; }
.file-name .icon { margin-right: 8px; color: #e74c3c; } /* PDF 红色图标 */
.text-muted { color: #999; font-size: 0.9rem; }
.status-badge { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; background: #e8f5e9; color: #2e7d32; }
.engine-tag { background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
.empty-text { text-align: center; color: #999; padding: 40px; }

/* 弹窗样式 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; width: 500px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
.modal-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }
.modal-body { padding: 30px 20px; }
.modal-footer { padding: 15px 20px; background: #f8f9fa; display: flex; justify-content: flex-end; gap: 10px; }

/* 上传区域 */
.upload-zone { border: 2px dashed #ddd; border-radius: 8px; padding: 30px; text-align: center; cursor: pointer; transition: 0.3s; background: #fafafa; }
.upload-zone:hover, .upload-zone.dragging { border-color: #42b983; background: #f0f9f5; }
.icon-cloud { font-size: 3rem; margin-bottom: 10px; color: #ddd; }
.hint { display: block; margin-top: 5px; color: #999; font-size: 0.8rem; }
.file-preview { display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-remove { background: none; border: none; color: #e74c3c; cursor: pointer; text-decoration: underline; font-size: 0.9rem; }

.status-message { margin-top: 15px; text-align: center; padding: 10px; border-radius: 6px; font-size: 0.9rem; }
.status-message.success { background: #e8f5e9; color: #2e7d32; }
.status-message.error { background: #ffebee; color: #c62828; }
.status-message.info { background: #e3f2fd; color: #1976d2; }

/* 按钮微调 */
.btn-sm { padding: 6px 16px; font-size: 0.9rem; border-radius: 20px; }
.btn-text { background: none; color: #666; }
.btn-text:hover { background: #eee; }
</style>