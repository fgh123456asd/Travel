'''RAG索引阶段'''

import sys,os
# 把项目根目录加入 Python 的搜索路径，让 Python 能找到根目录下的 settings.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib,os,sqlite3
from datetime import datetime
import settings as config
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter,MarkdownHeaderTextSplitter

'''
用 SQLite 数据库记录已经处理过的 MD5 值，避免重复处理同一个文件/内容。
'''
def get_conn():
    os.makedirs("./db", exist_ok=True)
    return sqlite3.connect("./db/md5_cache.db", check_same_thread=False)


def init_md5_db():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS md5_cache(md5 TEXT PRIMARY KEY)
        ''')
        conn.commit()
    except Exception as e:
        print(f"初始化数据库失败: {e}")
    finally:
        conn.close()


def check_md5(md5: str) -> bool:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM md5_cache WHERE md5=?', (md5,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def save_md5(md5: str):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO md5_cache(md5) VALUES(?)', (md5,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def get_string_md5(s: bytes) -> str:
    """计算字符串的MD5值"""
    return hashlib.md5(s).hexdigest()

init_md5_db()


#--------------------------------------------------------------------------------------------
'''
将用户上传的文本：切片-->embedding向量化-->存入 Chroma 向量数据库-->并做 MD5 去重
上传文本 → 计算MD5去重 → 已存在→跳过 / 不存在→继续
       → 根据文件类型（MD/普通）切分文本
       → MD文件：标题切分 → 递归切分 → 保留标题元数据
       → 普通文件：超长切分 / 短文本不切分
       → 给每个文本块绑定元数据（文件名/MD5/时间/标题）
       → 存入Chroma向量库 → 记录MD5 → 返回结果
'''
class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        '''
            创建一个 Chroma 向量数据库对象
            作用：1.存储文本向量  2.检索相似内容  3.做 RAG 知识库问答
        '''
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory
        )

        ''' 
            创建一个递归字符文本分割器RecursiveCharacterTextSplitter
        '''
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 每个文本块最大长度
            chunk_overlap=config.chunk_overlap,  # 相邻chunk重叠字符数
            separators=config.separators,  # 切分符号优先级
            length_function=len,
        )

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[   # 定义按哪些标题层级切分
                ("#", "一级标题"),
                ("##", "二级标题"),
                ("###", "三级标题"),
                ("####", "四级标题"),
            ],
            strip_headers=False,   # 不删除标题文本，保留在内容里
        )

    def upload_by_str(self, data: str, filename: str, file_bytes: bytes):
        # 1. MD5 去重
        md5_hex = get_string_md5(file_bytes)

        if check_md5(md5_hex):
            return "[跳过] 内容已经存在知识库中"

        # 2. 根据文件类型切分
        knowledge_chunks = []  #存储所有切分后的【文本内容】
        metadata = []    # 存储每个文本块对应的【元数据】（文件名、MD5、时间、标题等）
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   # 获取当前上传时间

        # Markdown 文件
        if filename.endswith(".md"):
            #先按 Markdown 标题层级切分（#/##/###），生成带标题元数据的文档对象
            md_docs = self.markdown_splitter.split_text(data)
            #再用递归字符切分器，把标题切分后的大块文本切成更小的标准块
            split_docs = self.text_splitter.split_documents(md_docs)

            # 遍历所有切分好的文档，提取文本+组装元数据
            for doc in split_docs:
                # 提取文档的纯文本内容，存入文本块列表
                knowledge_chunks.append(doc.page_content)
                # 复制并升级现有的元数据（包含一级标题、二级标题等）
                meta = doc.metadata.copy()
                # 追加自定义元数据：文件名、MD5、上传时间
                meta.update({
                    "filename": filename,
                    "md5": md5_hex,
                    "create_time": current_time
                })
                # 把完整元数据存入列表
                metadata.append(meta)

        else:
            # 其他文件
            if len(data) > config.max_split_char_number:
                knowledge_chunks = self.text_splitter.split_text(data)
            else:
                knowledge_chunks = [data]

            # 为每个文本块统一生成基础元数据（无标题信息）
            for chunk in knowledge_chunks:
                metadata.append({
                    "filename": filename,
                    "md5": md5_hex,
                    "create_time": current_time
                })

        # 3. 统一写入向量数据库
        if knowledge_chunks:
            self.chroma.add_texts(
                texts=knowledge_chunks,
                metadatas=metadata
            )
            save_md5(md5_hex)
            return "[成功]向量已保存到知识库中"
        else:
            return "[失败] 未能从文件中解析出任何有效文本"
