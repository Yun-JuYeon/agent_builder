import asyncio
import json
from fastapi import HTTPException, status
import httpx
from typing import AsyncGenerator, Optional

from pydantic import BaseModel


class RequestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    # payload 있으면 post, 없으면 get으로 요청
    async def post_client(self, url: str, payload: Optional[BaseModel|dict] = None):
        async with httpx.AsyncClient(timeout=30) as client:
            if payload: 
                if isinstance(payload, BaseModel):
                    payload = payload.model_dump(mode="json")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            else:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
    
    async def delete_client(self, url: str):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(url)
            response.raise_for_status()
            return response.json()

    # 스트리밍 응답 시 사용
    async def stream_chat(self, user_id: str, chat_request: dict) -> AsyncGenerator[str, None]:
        adk_run_url = f"{self.base_url}:30080/users/{user_id}/run_sse"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                async with client.stream("POST", adk_run_url, json=chat_request) as r:
                    async for chunk in r.aiter_text():
                        chunk = chunk.strip()
                        if not chunk.startswith("data:"):
                            raise RuntimeError(f"Chat stream failed: {chunk}")
                        try:
                            payload = json.loads(chunk[len("data:"):].strip())
                        except json.JSONDecodeError:
                            continue

                        if payload.get("partial") is True:
                            parts = payload.get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text")
                                if text:
                                    yield text
                            if not parts:
                                yield f"{json.dumps(payload, ensure_ascii=False)}\n"

        except asyncio.CancelledError:
            raise RuntimeError("Chat stream cancelled by client.")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Chat stream failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in chat stream: {e}")

