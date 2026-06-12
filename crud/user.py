from pydantic import EmailStr
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from cache.code import set_verify_code_cache, get_verify_code_cache, delete_verify_code_cache
from models.user import User
from schemas.user import RawPasswordStr, UsernameStr


# 创建验证码
async def create_code(email: str, code: str):
    return await set_verify_code_cache(email, code)

#检查邮箱验证码
async def check_email_code(email: str, code: str) -> bool:
    # 1. 从缓存获取正确验证码
    verify_code = await get_verify_code_cache(email)
    # 2. 验证码不存在 = 过期
    if not verify_code:
        return False
    # 3. 验证码不正确
    if verify_code != code:
        return False
    # 4. 验证成功 → **必须删除验证码，防止重复使用**
    await delete_verify_code_cache(email)
    return True


# 检查邮箱是否存在
async def email_is_exist(db: AsyncSession, email: str) -> bool:
    # 开启数据库事务
    async with db.begin():
        # 构建SQL查询：查询是否存在 邮箱=传入email 的用户
        stmt = select(exists().where(User.email == email))
        # 执行查询，并返回结果（True/False）
        return await db.scalar(stmt)

# 创建用户
async def create_user(db: AsyncSession,
                      email:EmailStr,
                      password: RawPasswordStr,
                      username: UsernameStr):
    async with db.begin():
        user = User(email=email, password=password, username=username)
        db.add(user)
        return user



#-----------------------------------------------------------------------------------------

async def get_by_email(db: AsyncSession, email: str):
    async with db.begin():
        # 构建SQL查询：查询是否存在 邮箱=传入email 的用户
        stmt = select(User).where(User.email==email)
        # 执行查询，并返回结果
        return await db.scalar(stmt)



