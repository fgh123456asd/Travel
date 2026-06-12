import os
from datetime import timedelta

# 数据库配置 - 从环境变量读取，部署时设置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:456123@localhost:3306/travel?charset=utf8mb4")

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# 邮件相关配置
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "3265597795@qq.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "ucorrbgomyiqcjdc")
MAIL_FROM = os.getenv("MAIL_FROM", "3265597795@qq.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "齐鲁途智")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"

# JWT 配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "asdasd2udyfjx")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "15")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30")))

# 图片基础 URL - 生产环境需修改
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "http://127.0.0.1:8000")

# ChromaDB 向量数据库
collection_name = os.getenv("COLLECTION_NAME", "sd_travel")
persist_directory = os.getenv("PERSIST_DIRECTORY", "./chroma.db")

# Embedding 模型
embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v2")

# 文本分割器配置
chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
max_split_char_number = int(os.getenv("MAX_SPLIT_CHAR_NUMBER", "1000"))
separators = [
    "\n\n", "\n", "。", "！", "？", "；", "，", "!", "?", ";", ",", " ", ".",
]

# AI API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# 前端地址（用于 CORS）
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
