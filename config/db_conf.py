from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
import settings

# 从 settings 读取数据库 URL（支持环境变量）
ASYNC_DATABASE_URL = settings.DATABASE_URL

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # 生产环境关闭 SQL 日志
    pool_size=10,
    max_overflow=20
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
