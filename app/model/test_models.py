from typing import Optional
import uuid

from pydantic import BaseModel

class TestRequest(BaseModel):
    id: uuid.UUID
    query: str

class TestResponse(BaseModel):
    id: uuid.UUID
    message: Optional[str] = ""