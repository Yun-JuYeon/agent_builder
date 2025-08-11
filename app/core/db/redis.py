import asyncio
import redis.asyncio as redis

from app.config import settings

# 비동기 Redis 클라이언트 생성
redis_client = redis.Redis(
    host=settings.RD_HOST,
    port=settings.RD_PORT,
    password=settings.RD_PASSWORD,
    decode_responses=True
)

# Redis 연결 테스트 함수 (비동기)
async def try_redis_server_connect():
    try:
        pong = await redis_client.ping()
        print("✅ Redis 연결:", pong)

        keys = await redis_client.keys('*')  # 모든 키 조회
        print("📦 Redis 키 목록:", keys)

    except redis.AuthenticationError:
        print("❌ Redis 인증 실패 - 비밀번호를 확인하세요!")
    finally:
        await redis_client.close()

# 진입점
if __name__ == "__main__":
    asyncio.run(try_redis_server_connect())
