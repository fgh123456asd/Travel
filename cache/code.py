from config.cache_conf import get_cache, set_cache, delete_cache


VERIFY_CODE_PREFIX = "verify:email:"  # 验证码 key 前缀


# 获取验证码缓存
async def get_verify_code_cache(email: str):
    key = f"{VERIFY_CODE_PREFIX}{email}"
    return await get_cache(key)  # 验证码是字符串 → 用 get_cache


# 写入验证码缓存（自动过期）
# 验证码过期时间：120秒（2分钟）→ 符合你注释里的规范
async def set_verify_code_cache(email: str, code: str, expire: int = 120):
    key = f"{VERIFY_CODE_PREFIX}{email}"
    return await set_cache(key, code, expire)


# 删除验证码缓存（验证成功后删除）
async def delete_verify_code_cache(email: str):
    key = f"{VERIFY_CODE_PREFIX}{email}"
    return await delete_cache(key)