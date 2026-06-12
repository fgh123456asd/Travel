# pip install streamlit
# 启动 streamlit run 文件
import time
import streamlit as st
from knowledge_base import KnowledgeBaseService

# 1. 页面初始化与组件渲染
# （1）添加页面标题
st.title("知识库更新服务")

# （2）添加文件上传组件--file_uploader
uploader_file=st.file_uploader(
    "请上传文件",
    type=["txt", "pdf", "md", "docx"],
    accept_multiple_files=False,  # 是否允许上传多个文件，一次只能上传一个文件
    key="file_uploader"            # 为该组件指定一个唯一的 key，方便在 session_state 中跟踪
)

# 2. 知识库服务实例化与状态管理
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

# 每次都从 session_state 中获取对象
service = st.session_state["service"]


# 判断用户是否已经上传了文件。如果没有上传，uploader_file 的值为 None
if uploader_file is not None:
    #提取并展示文件元数据
    file_name = uploader_file.name  # 获取上传文件的文件名（例如: "济南旅游攻略.txt"）
    file_size = uploader_file.size  # 获取上传文件的大小（字节数）
    file_type = uploader_file.type  # 获取文件的 MIME 类型（例如: "text/plain"）

    # st.subheader 在前端渲染一个小标题（H3 标签），这里用 f-string 动态展示文件名
    st.subheader(f"文件名: {file_name}")
    # st.write 是万能输出组件，:.2f 表示保留两位小数
    st.write(f"格式：{file_type} ，大小：{file_size:.2f}KB")

# ---  读取文件内容并解码 ---
    # uploader_file.getvalue() 会把上传的文件一次性以二进制字节流（bytes）的形式读入内存
    file_bytes = uploader_file.getvalue()

    # 将二进制字节流使用 utf-8 编码解码为 Python 的字符串（str）
    # 这样大模型或文本切分器（Text Splitter）才能识别
    text = file_bytes.decode("utf-8")

# --- 调用后端服务写入知识库 ---
    # st.spinner 是一个上下文管理器，包裹在里面的代码在执行时，前端会显示一个“转圈圈”的加载动画
    with st.spinner("载入知识库中。。。。。"):
        # 强制线程休眠 1 秒（通常用于模拟网络延迟或纯粹为了让加载动画显眼一点，实际生产中可去掉）
        time.sleep(1)

        # 【核心 RAG 触发点】
        # 传入参数：解析后的文本字符串、文件名、原始字节流
        # 该方法内部通常会执行：文本切片 -> Embedding 向量化 -> 存入向量数据库
        result = service.upload_by_str(text, file_name, file_bytes)

        # 将后端服务返回的结果（如 "上传成功"、"去重成功" 或错误信息）直接打印在网页上
        st.write(result)