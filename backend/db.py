# db.py
from sqlalchemy import create_engine, text
import uuid

# 数据库
MYSQL_URL = "mysql+mysqlconnector://rag:Ly6fHrM5tCNxryLB@115.120.241.249:3306/rag"

# 创建全局的连接池
engine = create_engine(MYSQL_URL, pool_recycle=3600)

def save_document_record(filename: str):
    """记录上传的文件信息"""
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO documents (filename) VALUES (:filename)"),
            {"filename": filename}
        )
        conn.commit()


def save_chat_history(question: str, answer: str, kb_id: int, temperature: float, top_k: int):
    """记录问答历史及当时的参数设置"""
    try:
        with engine.connect() as conn:
            # 插入用户提问记录 (带参数)
            conn.execute(
                text("""
                     INSERT INTO chat_history (role, content, kb_id, temperature, top_k)
                     VALUES ('user', :q, :kb_id, :temp, :top_k)
                     """),
                {"q": question, "kb_id": kb_id, "temp": temperature, "top_k": top_k}
            )

            # 插入 AI 回答记录 (带参数，保持上下文一致)
            conn.execute(
                text("""
                     INSERT INTO chat_history (role, content, kb_id, temperature, top_k)
                     VALUES ('assistant', :a, :kb_id, :temp, :top_k)
                     """),
                {"a": answer, "kb_id": kb_id, "temp": temperature, "top_k": top_k}
            )
            conn.commit()
    except Exception as e:
        print(f"数据库写入错误: {e}")


# 新增查询函数：获取历史记录
def get_chat_history(limit: int = 50):
    """获取最近的聊天记录"""
    with engine.connect() as conn:
        # 按时间正序排列
        result = conn.execute(
            text("""
                 SELECT role, content, kb_id, temperature, top_k, created_at
                 FROM chat_history
                 ORDER BY created_at ASC LIMIT :limit
                 """),
            {"limit": limit}
        )

        history = []
        for row in result:
            history.append({
                "role": row[0],
                "content": row[1],
                "kb_id": row[2],
                "temperature": row[3],
                "top_k": row[4],
                "created_at": str(row[5])
            })
        return history


def create_session(first_question: str):
    """创建一个新会话，标题默认是第一个问题的前20个字"""
    session_id = str(uuid.uuid4())
    title = first_question[:20] if first_question else "新对话"

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO chat_sessions (id, title) VALUES (:id, :title)"),
            {"id": session_id, "title": title}
        )
        conn.commit()
    return session_id


def get_sessions():
    """获取会话列表"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, created_at FROM chat_sessions ORDER BY updated_at DESC"))
        return [{"id": row[0], "title": row[1], "created_at": str(row[2])} for row in result]


def get_chat_history_by_session(session_id: str, limit: int = 10):
    """获取指定会话的上下文记录 (用于传给大模型)"""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                 SELECT role, content
                 FROM chat_history
                 WHERE session_id = :sid
                 ORDER BY created_at ASC 
                     LIMIT :limit
                 """),
            {"sid": session_id, "limit": limit}
        )
        # 转换为 LangChain 友好的格式
        return [{"role": row[0], "content": row[1]} for row in result]


def save_chat_record(session_id: str, role: str, content: str, kb_id: int, temperature: float, top_k: int):
    """保存单条消息"""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                     INSERT INTO chat_history (session_id, role, content, kb_id, temperature, top_k)
                     VALUES (:sid, :role, :content, :kb_id, :temp, :top_k)
                     """),
                {
                    "sid": session_id, "role": role, "content": content,
                    "kb_id": kb_id, "temp": temperature, "top_k": top_k
                }
            )
            # 更新会话的 updated_at 时间
            conn.execute(
                text("UPDATE chat_sessions SET updated_at = NOW() WHERE id = :sid"),
                {"sid": session_id}
            )
            conn.commit()
    except Exception as e:
        print(f"数据库保存失败: {e}")