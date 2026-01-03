import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# 导入修改后的模块
import db
from rag_service import rag_service
from schemas import KBCreateRequest, KBResponse, ChatRequest, UploadResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 知识库管理接口 ---

@app.post("/kb/create", response_model=KBResponse)
async def create_kb(kb: KBCreateRequest):
    """创建新知识库"""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("INSERT INTO knowledge_bases (name, description) VALUES (:name, :desc)"),
            {"name": kb.name, "desc": kb.description}
        )
        conn.commit()
        new_id = result.lastrowid
        return {"id": new_id, "name": kb.name, "description": kb.description, "created_at": str(os.times())}


@app.get("/kb/list")
async def list_kbs():
    """获取知识库列表"""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, description, created_at FROM knowledge_bases ORDER BY created_at DESC")
        )
        # 将结果转为字典列表
        kbs = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": str(row[3])
            }
            for row in result
        ]
    return kbs


# --- 文件上传接口 ---

@app.post("/upload")
async def upload_pdf(
        file: UploadFile = File(...),
        kb_id: int = Form(...)
):
    temp_filename = f"temp_{file.filename}"
    try:
        # 保存临时文件
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. 解析入库
        rag_service.ingest_file(temp_filename, kb_id)

        # 2. 数据库记录
        with db.engine.connect() as conn:
            conn.execute(
                text("INSERT INTO documents (filename, kb_id) VALUES (:filename, :kb_id)"),
                {"filename": file.filename, "kb_id": kb_id}
            )
            conn.commit()

        return {"status": "success", "message": "上传并解析成功"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# 获取历史记录接口
@app.get("/kb/{kb_id}/files")
async def list_files_in_kb(kb_id: int):
    """获取指定知识库下的所有文件"""
    with db.engine.connect() as conn:
        # 按照上传时间倒序排列
        result = conn.execute(
            text("SELECT id, filename, status, upload_time FROM documents WHERE kb_id = :kb_id ORDER BY upload_time DESC"),
            {"kb_id": kb_id}
        )
        files = [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "upload_time": str(row[3])
            }
            for row in result
        ]
    return files


@app.get("/chat/history")
async def get_history():
    try:
        history = db.get_chat_history(limit=100)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 聊天接口
@app.get("/sessions")
async def list_sessions():
    """获取左侧会话列表"""
    return db.get_sessions()


@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """点击某个会话时，加载它的历史消息"""
    return db.get_chat_history_by_session(session_id, limit=100)


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # 1. 如果没有 session_id，说明是新对话，先创建 session
        current_session_id = request.session_id
        if not current_session_id:
            current_session_id = db.create_session(request.question)

        # 2. 从数据库获取该会话的历史记录 (实现上下文记忆)
        history = db.get_chat_history_by_session(current_session_id, limit=request.history_len)

        # 3. 调用 RAG 服务 (传入 history)
        answer = rag_service.query(
            question=request.question,
            kb_id=request.kb_id,
            history=history,  # 🟢 传入历史
            temperature=request.temperature,
            top_k=request.top_k
        )

        # 4. 保存记录
        db.save_chat_record(current_session_id, 'user', request.question, request.kb_id, request.temperature,
                            request.top_k)
        db.save_chat_record(current_session_id, 'assistant', answer, request.kb_id, request.temperature, request.top_k)

        return {
            "answer": answer,
            "session_id": current_session_id  # 返回 ID 给前端，以便前端锁定当前会话
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))