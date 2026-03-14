from core.database import AsyncSessionLocal
from core.cache import redis_client

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_cache():
    return redis_client