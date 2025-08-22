import json
from typing import Any
from pydantic import BaseModel

def sse_event(event: str, data: Any) -> str:
    if isinstance(data, BaseModel):  # Pydantic 모델이면
        data = data.model_dump(mode="json")
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
