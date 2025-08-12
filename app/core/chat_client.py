import json
import httpx
from typing import AsyncGenerator

class AgentChatClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def stream_chat(self, port: str, chat_request: dict) -> AsyncGenerator[str, None]:
        adk_run_url = f"{self.base_url}:{port}/run_sse"
        async with httpx.AsyncClient(timeout=30) as client:
            async with client.stream("POST", adk_run_url, json=chat_request) as r:
                async for chunk in r.aiter_text():
                    chunk = chunk.strip()
                    if not chunk.startswith("data:"):
                        continue
                    try:
                        payload = json.loads(chunk[len("data:"):].strip())
                    except json.JSONDecodeError:
                        continue
                    
                    if payload.get("partial") is True:
                        parts = payload.get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text")
                            if text:
                                yield f"data: {text}\n\n"
