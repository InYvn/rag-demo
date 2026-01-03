<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">RAGDemo</div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/kb">知识库</router-link>
        <router-link to="/chat">对话</router-link>
      </div>
    </nav>
    <div class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
/* 全局基础样式 */
body { margin: 0; background: #f5f7fa; font-family: 'Helvetica Neue', Arial, sans-serif; }
.navbar { background: #fff; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.nav-brand { font-size: 1.2rem; font-weight: bold; color: #42b983; }
.nav-links a { margin-left: 20px; text-decoration: none; color: #666; font-weight: 500; }
.nav-links a.router-link-active { color: #42b983; }
.container {  margin: 30px auto; padding: 0 20px; }
/* 公用卡片样式 */
.card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1); margin-bottom: 20px; }
.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; transition: 0.3s; }
.btn-primary { background: #42b983; color: white; }
.btn-primary:hover { opacity: 0.9; }
input, select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
</style>