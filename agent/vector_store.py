import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
import settings as config

class VectorStoresService(object):
    """
       向量数据库服务类
       负责：
       1. 创建 Chroma 向量库
       2. 管理向量数据
       3. 提供 Retriever 给 RAG 使用
    """
    def __init__(self, embedding):
        """
               初始化向量数据库
               参数：
                   embedding : 向量模型对象
                               例如：
                               DashScopeEmbeddings()
                               OpenAIEmbeddings()
               """
        self.embedding = embedding
        # 创建 Chroma 向量数据库实例
        self.vectotr_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=embedding,
            persist_directory=config.persist_directory
        )

    def get_retriever(self):
        """
                获取检索器（Retriever）
                返回：
                    VectorStoreRetriever对象
                用于：
                    query -> 向量化 -> 相似度搜索 -> 返回相关文档
        """
        return self.vectotr_store.as_retriever(search_kwargs={"k":3})



