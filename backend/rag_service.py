import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 配置
CHROMA_PATH = "./chroma_db"
ZHIPU_API_KEY = "您的_ZHIPU_API_KEY"

class RAGService:
    def __init__(self):
        # 1. Embedding 模型 (BGE-Large) - 只需要加载一次
        print("正在加载 BGE-Large 模型...")
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")

    def _get_vector_db(self, kb_id: int):
        """
        根据知识库ID，获取对应的 Chroma 集合
        """
        collection_name = f"kb_collection_{kb_id}"
        return Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )

    def ingest_file(self, file_path: str, kb_id: int):
        """入库时，必须指定 kb_id"""
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)

        # 获取对应的向量库集合
        vector_db = self._get_vector_db(kb_id)

        vector_db.add_documents(documents=splits)
        return len(splits)

    def format_history(self, history_list):
        """将数据库查出来的历史记录转为字符串，供 Prompt 使用"""
        formatted_str = ""
        for msg in history_list:
            role = "用户" if msg['role'] == 'user' else "AI助手"
            formatted_str += f"{role}: {msg['content']}\n"
        return formatted_str

    def query(self, question: str, kb_id: int, history: list, temperature: float = 0.1, top_k: int = 3) -> str:
        """
        核心逻辑：接收 history 参数，实现多轮对话
        """
        vector_db = self._get_vector_db(kb_id)
        retriever = vector_db.as_retriever(search_kwargs={"k": top_k})

        template = """你是一个智能助手。请结合以下“历史对话”和“上下文”，回答用户最新的问题。

        【历史对话】
        {chat_history}

        【上下文知识】
        {context}

        【用户最新问题】
        {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # 格式化历史记录
        history_str = self.format_history(history)

        # 构建 LLM
        llm = ChatOpenAI(
            model_name="glm-4.5-flash",
            openai_api_key=ZHIPU_API_KEY,
            openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
            temperature=temperature
        )

        # LCEL
        rag_chain = (
                {
                    "context": retriever | format_docs,
                    "chat_history": lambda x: history_str,
                    "question": RunnablePassthrough()
                }
                | prompt
                | llm
                | StrOutputParser()
        )

        return rag_chain.invoke(question)


rag_service = RAGService()