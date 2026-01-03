# RAGDemo - 本地部署指南

**RAGDemo** 是一个轻量级的企业级知识库问答系统原型。
它采用前后端分离架构，前端使用 **Vue 2** 构建现代化 Dashboard 界面，后端使用 **FastAPI** 结合 **LangChain** 实现 RAG（检索增强生成）逻辑，支持多知识库管理、多会话记忆以及参数动态调整。

## ✨ 功能特性

**RAGDemo** 提供了一套完整的 RAG（检索增强生成）解决方案，旨在以最低的成本实现高质量的私有知识库问答。

### 📚 1. 知识库管理 
* **多库隔离**：支持创建多个独立的知识库（如“产品手册”、“技术文档”），数据互不干扰。
* **PDF 解析**：支持上传 PDF 文档，系统自动使用 `LangChain` 进行文本切片与清洗。
* **本地向量化**：集成 **BGE-Large (zh)** 模型，在本地进行 Embedding 向量化，**无需消耗 Token 费用**，且保障数据隐私。
* **高性能存储**：使用 ChromaDB 存储向量数据，检索速度快，准确率高。

### 💬 2. 智能上下文问答 
* **多轮对话记忆**：系统能够记住当前会话的历史上下文（基于 MySQL 存储），支持追问（如“它有哪些特点？”）。
* **精准检索**：基于语义相似度检索最相关的文档片段，大幅减少大模型的幻觉问题。
* **混合模型架构**：
    * **Embedding**: 本地 BGE 模型（免费、私有）。
    * **LLM**: 智谱 GLM-4-Flash（高速、低成本）。

### ⚙️ 3. 动态参数调优
* **可视化配置**：在聊天窗口右侧实时调整 RAG 参数，无需重启服务。
    * **Temperature (温度)**：控制回答的随机性（0.1 严谨 / 0.8 创意）。
    * **Top-K (引用数)**：控制每次回答参考的文档片段数量（1-10）。
* **知识库热切换**：在对话过程中随时切换引用的知识库，灵活应对不同话题。

### 🗂️ 4. 会话管理系统
* **历史记录持久化**：所有对话记录均存储于 MySQL，刷新页面不丢失。
* **多会话切换**：左侧侧边栏展示历史会话列表，支持新建对话和快速切换旧对话。

## 📂 项目结构说明

在开始部署前，请先了解一下项目的目录结构及其作用，以便于后续维护：

```text
RAGDemo/
├── backend/                  # [后端] Python 服务端代码
│   ├── main.py               # 程序入口，定义了所有 API 接口 (FastAPI)
│   ├── rag_service.py        # RAG 核心业务逻辑 (LangChain, ChromaDB, 模型调用)
│   ├── db.py                 # 数据库层，处理 MySQL 连接与 CRUD 操作
│   ├── schemas.py            # 数据校验模型 (Pydantic)，定义前后端交互的数据格式
│   ├── requirements.txt      # 后端依赖包列表
│   └── chroma_db/            # (自动生成) 向量数据库的本地存储文件夹
│
├── frontend/                 # [前端] Vue 2 客户端代码
│   ├── src/
│   │   ├── utils/
│   │   │   └── request.js    # Axios 封装，修改后端 IP 地址在这里配置
│   │   ├── router/
│   │   │   └── index.js      # 路由配置 (定义页面跳转规则)
│   │   ├── views/            # 页面组件文件夹
│   │   │   ├── Home.vue      # 首页 Dashboard
│   │   │   ├── Chat.vue      # 聊天窗口 (包含左侧列表、中间对话、右侧参数)
│   │   │   ├── KBList.vue    # 知识库列表管理页
│   │   │   └── KBDetail.vue  # 知识库详情页 (文件上传与列表)
│   │   ├── App.vue           # 根组件 (处理全局布局)
│   │   └── main.js           # 前端入口文件
│   └── package.json          # 前端依赖配置
│
└── README.md                 # 项目说明文档
```

---

## 📋 部署步骤目录
1. [环境准备](#1-环境准备)
2. [后端部署](#2-后端部署)
3. [数据库初始化](#3-数据库初始化)
4. [配置修改 (关键)](#4-配置修改-关键)
5. [前端部署](#5-前端部署)
6. [局域网访问](#6-局域网访问)

---

## 1. 环境准备

确保您的服务器或本地电脑已安装以下基础环境：
* **Python**: 3.10 或 3.12 (推荐使用 Conda 管理环境)
* **Node.js**: v14 或 v16 (用于 Vue 前端编译)
* **MySQL**: 5.7 或 8.0 (用于存储结构化数据)

---

## 2. 后端部署

### 2.1 创建虚拟环境
推荐使用 Conda 创建独立环境，避免依赖冲突。

```bash
# 创建名为 rag 的环境
conda create -n rag python=3.12

# 激活环境
conda activate rag
```

### 2.2 安装依赖
进入 `backend` 目录，安装 Python 依赖包。

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. 数据库初始化

请登录您的 MySQL 数据库，创建一个新的数据库（例如 `rag`），然后执行以下 SQL 语句以创建必要的表结构。

```sql
-- 1. 创建数据库
CREATE DATABASE rag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rag;

-- 2. 创建知识库表
CREATE TABLE knowledge_bases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建文件记录表
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    kb_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'success',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
);

-- 4. 创建会话表 (Session - 用于左侧历史记录)
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 5. 创建聊天记录表 (History - 包含参数快照)
CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT,
    kb_id INT,
    temperature FLOAT,
    top_k INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
);

-- 6. 初始化默认知识库
INSERT INTO knowledge_bases (name, description) VALUES ('默认知识库', '系统初始化默认库');
```

---

## 4. 配置修改 (关键)

在运行前，**必须**修改以下配置文件中的参数为您的真实信息。

### 4.1 修改数据库连接 (`backend/db.py`)
找到 `MYSQL_URL` 变量，修改为您的 MySQL 用户名、密码和 IP。

```python
# 格式: mysql+mysqlconnector://用户名:密码@IP地址:端口/数据库名
MYSQL_URL = "mysql+mysqlconnector://root:您的密码@localhost:3306/rag"
```

### 4.2 修改 API Key (`backend/rag_service.py`)
找到 `ZHIPU_API_KEY` 变量，填入您的智谱 AI API Key（用于 LLM 对话）。

```python
# 必须以 sk- 开头
ZHIPU_API_KEY = "您的_ZHIPU_API_KEY"
```
*注意：Embedding 模型已配置为本地模型 (BGE-Large)，不需要修改 Key，但第一次运行时会自动下载模型 (约 1.2GB)，请保持网络通畅。*

### 4.3 修改前端请求地址 (`frontend/src/utils/request.js`)
如果您需要局域网访问，请将 IP 修改为您的本机局域网 IP (如 `192.168.x.x`)。

```javascript
// src/utils/request.js
// const BASE_URL = 'http://localhost:8000'; // 仅本机访问
const BASE_URL = 'http://192.168.1.5:8000'; // 如需局域网访问，改为本机真实 IP
```

### 4.4 **后端启动命令**：
```bash
# 在 backend 目录下
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 5. 前端部署

进入 `frontend` 目录，安装 Node.js 依赖并启动。

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

成功后，浏览器访问控制台显示的地址 (通常是 `http://localhost:8080`) 即可看到界面。

---

### 常见问题排查

* **报错 `ModuleNotFoundError`**: 请检查是否在终端中激活了 conda 环境 (`conda activate rag`)。
* **报错 `Access denied for user`**: 请检查 `backend/db.py` 中的 MySQL 密码是否正确，以及用户是否有权限。
* **一直显示“正在加载本地模型”**: 第一次运行后端时需要从 HuggingFace 下载 BGE 模型，请耐心等待下载完成。
* **前端报错 `Network Error`**: 请检查 `request.js` 中的 IP 是否正确，以及后端是否已启动。