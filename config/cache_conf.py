import redis.asyncio as redis
import json
from typing import Any
import settings

# 从 settings 读取 Redis 配置（支持环境变量）
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存数据失败：{e}")
        return None

async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取JSON缓存数据失败：{e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, expire)
        return True
    except Exception as e:
        print(f"设置缓存数据失败：{e}")
        return False

async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"删除缓存数据失败：{e}")
        return False
