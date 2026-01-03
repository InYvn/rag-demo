from pydantic import BaseModel
from typing import Optional


# --- 1. 基础响应模型 ---
class UploadResponse(BaseModel):
    status: str
    message: str


# --- 2. 知识库管理模型 ---
class KBBase(BaseModel):
    name: str
    description: Optional[str] = None


class KBCreateRequest(KBBase):
    """创建知识库时的请求参数"""
    pass


class KBResponse(KBBase):
    """返回给前端的知识库信息"""
    id: int
    created_at: str

    class Config:
        from_attributes = True


# --- 3. 聊天相关模型  ---
class ChatRequest(BaseModel):
    question: str
    kb_id: int  # 必选：指定要在哪个知识库里搜
    session_id: Optional[str] = None  # 如果是新对话则为 None
    history_len: int = 10  # 可选：携带多少轮历史对话
    temperature: float = 0.1  # 可选：控制模型回答的随机性 (0-1)
    top_k: int = 3  # 可选：引用多少个文档片段